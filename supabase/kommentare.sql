-- =====================================================================
-- WOSOINSIDER: Kommentare (Supabase / Postgres)
-- Stand 28.10.2026
--
-- Einmal komplett im Supabase SQL Editor ausführen ("Run").
-- Darf erneut ausgeführt werden: Tabellen bleiben, Funktionen und
-- Regeln werden aktualisiert, Startwerte nicht überschrieben.
--
-- Prinzip
-- * Lesen geht ohne Anmeldung.
-- * Schreiben, Liken, Melden braucht eine Sitzung. Am Anfang ist das
--   eine anonyme Sitzung (Supabase "Anonymous Sign-Ins"). Dieselbe
--   Nutzer-ID wird später per Mail, Apple oder Google zu einem echten
--   Konto. Kommentare, Name und Likes bleiben dabei erhalten.
-- * Alle Regeln (Tempo, Wortfilter, Sperren, Meldeschwelle) laufen in
--   der Datenbank. Die App oder Webseite kann sie nicht umgehen.
-- * Schalter in der Tabelle public.einstellung, ohne Code-Änderung.
-- =====================================================================

begin;

-- ---------------------------------------------------------------------
-- 1. Einstellungen
-- ---------------------------------------------------------------------
create table if not exists public.einstellung (
  schluessel text primary key,
  wert       text not null,
  info       text
);

insert into public.einstellung (schluessel, wert, info) values
  ('kommentare_an',    'ja',  'Notschalter. nein = niemand kann schreiben, Lesen geht weiter'),
  ('meldeschwelle',    '3',   'Ab so vielen Meldungen verschiedener Nutzer wird ein Kommentar automatisch ausgeblendet'),
  ('abstand_sekunden', '30',  'Mindestabstand zwischen zwei Kommentaren desselben Nutzers'),
  ('max_pro_stunde',   '15',  'Höchstens so viele Kommentare pro Nutzer und Stunde'),
  ('max_pro_tag',      '60',  'Höchstens so viele Kommentare pro Nutzer und Tag'),
  ('neue_pruefen',     'nein','ja = Kommentare neuer Nutzer (Vertrauen 0) erst nach Freigabe sichtbar'),
  ('links_pruefen',    'ja',  'ja = Kommentare mit Links erst nach Freigabe sichtbar'),
  ('anonym_schreiben', 'ja',  'nein = nur Nutzer mit echtem Konto (Mail/Apple/Google) dürfen schreiben')
on conflict (schluessel) do nothing;

alter table public.einstellung enable row level security;
drop policy if exists einstellung_lesen on public.einstellung;
create policy einstellung_lesen on public.einstellung for select to anon, authenticated using (true);
revoke all on public.einstellung from anon, authenticated;
grant select on public.einstellung to anon, authenticated;

create or replace function public.einst(k text) returns text
language sql stable security definer set search_path = '' as $$
  select wert from public.einstellung where schluessel = k
$$;

-- ---------------------------------------------------------------------
-- 2. Profile (eins pro Nutzer, auch für anonyme Sitzungen)
-- ---------------------------------------------------------------------
create table if not exists public.profil (
  id           uuid primary key references auth.users(id) on delete cascade,
  name         text not null unique check (char_length(name) between 3 and 24),
  rolle        text not null default 'nutzer' check (rolle in ('nutzer', 'moderator', 'admin')),
  vertrauen    smallint not null default 0 check (vertrauen between 0 and 2),
  gesperrt_bis timestamptz,
  sperrgrund   text,
  schatten     boolean not null default false,
  erstellt     timestamptz not null default now()
);

alter table public.profil add column if not exists name_gewaehlt boolean not null default false;
alter table public.profil add column if not exists name_aenderungen smallint not null default 0;
-- Verifiziert-Haken (blauer Haken wie bei Instagram): Redaktion automatisch, später z. B. Vereine oder Spielerinnen
alter table public.profil add column if not exists verifiziert boolean not null default false;

alter table public.profil enable row level security;
drop policy if exists profil_lesen on public.profil;
create policy profil_lesen on public.profil for select to anon, authenticated using (true);
revoke all on public.profil from anon, authenticated;
-- Öffentlich nur Name und Rolle (für das Abzeichen "Redaktion")
grant select (id, name, rolle, verifiziert) on public.profil to anon, authenticated;

-- Neuer Nutzer (auch anonym) bekommt einen Platzhalternamen wie "WoSo-Fan 1704".
-- Beim ersten Kommentar wählt er seinen Namen (oder behält diesen), danach ist genau eine Änderung möglich.
create or replace function public.profil_anlegen() returns trigger
language plpgsql security definer set search_path = '' as $$
declare n text; i int := 0;
begin
  loop
    n := 'WoSo-Fan ' || case when i < 15 then lpad(floor(random() * 10000)::int::text, 4, '0')
                                else lpad(floor(random() * 1000000)::int::text, 6, '0') end;
    exit when not exists (select 1 from public.profil where name = n);
    i := i + 1;
    if i > 25 then n := 'WoSo-Fan ' || substr(replace(new.id::text, '-', ''), 1, 10); exit; end if;
  end loop;
  insert into public.profil (id, name) values (new.id, n) on conflict (id) do nothing;
  return new;
end $$;

drop trigger if exists wi_profil_anlegen on auth.users;
create trigger wi_profil_anlegen after insert on auth.users
  for each row execute function public.profil_anlegen();

-- Profile für Nutzer anlegen, die es schon vor diesem Skript gab
insert into public.profil (id, name)
select u.id, 'WoSo-Fan ' || substr(replace(u.id::text, '-', ''), 1, 10)
from auth.users u
where not exists (select 1 from public.profil p where p.id = u.id)
on conflict do nothing;

-- Hilfsfunktionen
create or replace function public.ist_anonym() returns boolean
language sql stable set search_path = '' as $$
  select coalesce((auth.jwt() ->> 'is_anonymous')::boolean, false)
$$;

create or replace function public.ist_mod() returns boolean
language sql stable security definer set search_path = '' as $$
  select exists (select 1 from public.profil where id = auth.uid() and rolle in ('moderator', 'admin'))
$$;

-- Moderieren darf: Moderator/Admin in App/Web oder Finn im SQL Editor (Nutzer postgres)
create or replace function public.darf_moderieren() returns boolean
language sql stable security definer set search_path = '' as $$
  select public.ist_mod() or (auth.uid() is null and session_user in ('postgres', 'supabase_admin'))
$$;

create or replace function public.ist_schatten(uid uuid) returns boolean
language sql stable security definer set search_path = '' as $$
  select coalesce((select schatten from public.profil where id = uid), false)
$$;

-- ---------------------------------------------------------------------
-- 3. Wortfilter
-- ---------------------------------------------------------------------
-- Text vereinheitlichen: klein, Umlaute ausgeschrieben, 0/1/3/4/5/7/@/$
-- wie Buchstaben, gedehnte Buchstaben ("duuuumm") zusammengezogen.
create or replace function public.normalisiere(t text) returns text
language sql immutable set search_path = '' as $$
  select regexp_replace(
           translate(
             replace(replace(replace(replace(replace(replace(lower(coalesce(t, '')), 'ä', 'ae'), 'ö', 'oe'), 'ü', 'ue'), 'ß', 'ss'), 'æ', 'ae'), 'þ', 'th'),
             '013457@$€áàâãåāéèêëēěíìîïīóòôõøōőúùûūůűýçćčñńňšśşžźżđðłğıăţřďťľĺŕ',
             'oieastaseaaaaaaeeeeeeiiiiiooooooouuuuuuycccnnnssszzzddlgiatrdtllr'),
           '(.)\1{2,}', '\1', 'g')
$$;

create table if not exists public.filterwort (
  wort      text primary key,
  wort_norm text generated always as (public.normalisiere(wort)) stored,
  aktion    text not null default 'pruefen' check (aktion in ('blocken', 'pruefen')),
  teilwort  boolean not null default false,  -- true = trifft auch innerhalb von Wörtern
  info      text
);
alter table public.filterwort enable row level security;
revoke all on public.filterwort from anon, authenticated;  -- Liste bleibt geheim

-- Startliste. blocken = wird gar nicht gespeichert, pruefen = landet in der Warteschlange.
-- Erweitern im Table Editor (Tabelle filterwort) oder per insert.
insert into public.filterwort (wort, aktion, teilwort, info) values
  ('hurensohn',   'blocken', true,  'Beleidigung'),
  ('hurentochter','blocken', true,  'Beleidigung'),
  ('fotze',       'blocken', true,  'Beleidigung'),
  ('wichser',     'blocken', true,  'Beleidigung'),
  ('missgeburt',  'blocken', true,  'Beleidigung'),
  ('schlampe',    'blocken', true,  'Beleidigung'),
  ('nutte',       'blocken', false, 'Beleidigung'),
  ('arschloch',   'blocken', true,  'Beleidigung'),
  ('bitch',       'blocken', false, 'Beleidigung'),
  ('drecksau',    'blocken', true,  'Beleidigung'),
  ('spast',       'blocken', false, 'Beleidigung'),
  ('mongo',       'blocken', false, 'Beleidigung'),
  ('schwuchtel',  'blocken', true,  'Hass'),
  ('kanake',      'blocken', true,  'Hass'),
  ('neger',       'blocken', false, 'Hass'),
  ('kys',         'blocken', false, 'Aufforderung zur Selbsttötung'),
  ('fick',        'blocken', false, 'Vulgär'),
  ('ficken',      'blocken', false, 'Vulgär'),
  ('heil hitler', 'blocken', true,  'Verfassungsfeindlich'),
  ('sieg heil',   'blocken', true,  'Verfassungsfeindlich'),
  ('behindert',   'pruefen', true,  'Kontext prüfen'),
  ('idiot',       'pruefen', true,  'Kontext prüfen'),
  ('nazi',        'pruefen', true,  'Kontext prüfen'),
  ('zigeuner',    'pruefen', true,  'Kontext prüfen'),
  ('umbringen',   'pruefen', true,  'Drohung?'),
  ('abstechen',   'pruefen', true,  'Drohung?'),
  ('vergewaltig', 'pruefen', true,  'Drohung?'),
  ('emanze',      'pruefen', true,  'Kontext prüfen'),
  ('casino',      'pruefen', true,  'Spam'),
  ('bitcoin',     'pruefen', true,  'Spam'),
  ('krypto',      'pruefen', true,  'Spam'),
  ('onlyfans',    'pruefen', true,  'Spam'),
  ('telegram',    'pruefen', true,  'Spam'),
  ('whatsapp',    'pruefen', true,  'Spam'),
  ('wettbonus',   'pruefen', true,  'Spam')
on conflict (wort) do nothing;

-- Liefert das erste getroffene Filterwort (blocken vor pruefen) oder nichts
create or replace function public.filter_treffer(t text, out wort text, out aktion text)
language plpgsql stable security definer set search_path = '' as $$
declare n text := public.normalisiere(t); f record;
begin
  for f in select fw.wort, fw.wort_norm, fw.aktion, fw.teilwort from public.filterwort fw
           order by (fw.aktion = 'blocken') desc, fw.wort loop
    if (f.teilwort and position(f.wort_norm in n) > 0)
       or (not f.teilwort and n ~ ('\m' || regexp_replace(f.wort_norm, '([.^$*+?()\[\]{}|\\])', '\\\1', 'g') || '\M')) then
      wort := f.wort; aktion := f.aktion; return;
    end if;
  end loop;
end $$;

-- ---------------------------------------------------------------------
-- 4. Kommentare
-- ---------------------------------------------------------------------
create table if not exists public.kommentar (
  id         uuid primary key default gen_random_uuid(),
  beitrag    text not null check (char_length(beitrag) between 1 and 120),  -- id der Meldung aus news.json
  autor      uuid not null default auth.uid() references public.profil(id) on delete cascade,
  eltern     uuid references public.kommentar(id) on delete cascade,        -- Antwort auf (nur eine Ebene)
  text       text not null check (char_length(text) between 1 and 1000),
  status     text not null default 'sichtbar'
             check (status in ('sichtbar', 'pruefung', 'ausgeblendet', 'geloescht')),
  grund      text,          -- Begründung bei pruefung/ausgeblendet, sieht die Autorin/der Autor
  likes      int not null default 0,
  meldungen  int not null default 0,
  erstellt   timestamptz not null default now()
);
-- Angeheftet (Redaktion): höchstens ein Kommentar je Meldung steht oben
alter table public.kommentar add column if not exists angeheftet boolean not null default false;
create index if not exists kommentar_beitrag_idx on public.kommentar (beitrag, erstellt desc);
create index if not exists kommentar_autor_idx   on public.kommentar (autor, erstellt desc);
create index if not exists kommentar_eltern_idx  on public.kommentar (eltern);
create index if not exists kommentar_offen_idx   on public.kommentar (status) where status in ('pruefung', 'ausgeblendet');

-- Alle Regeln beim Schreiben
create or replace function public.kommentar_regeln() returns trigger
language plpgsql security definer set search_path = '' as $$
declare p public.profil; e public.kommentar; f record; n int;
begin
  -- Felder, die Nutzer nicht selbst setzen dürfen
  new.autor := auth.uid();
  new.status := 'sichtbar'; new.grund := null; new.likes := 0; new.meldungen := 0; new.erstellt := now();
  new.angeheftet := false;

  if new.autor is null then raise exception 'WI_LOGIN' using hint = 'Keine Sitzung'; end if;
  if public.einst('kommentare_an') is distinct from 'ja' then raise exception 'WI_AUS'; end if;
  if public.ist_anonym() and public.einst('anonym_schreiben') is distinct from 'ja' then raise exception 'WI_KONTO'; end if;

  select * into p from public.profil where id = new.autor;
  if not found then raise exception 'WI_LOGIN'; end if;
  if p.gesperrt_bis is not null and p.gesperrt_bis > now() then raise exception 'WI_GESPERRT'; end if;

  -- Text säubern: Ränder, mehr als eine Leerzeile, Steuerzeichen
  new.text := btrim(regexp_replace(regexp_replace(new.text, '[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', 'g'), '\n{3,}', E'\n\n', 'g'));
  if char_length(new.text) < 2 then raise exception 'WI_KURZ'; end if;

  -- Antworten: nur auf sichtbare Hauptkommentare desselben Beitrags
  if new.eltern is not null then
    select * into e from public.kommentar where id = new.eltern;
    if not found or e.eltern is not null or e.beitrag <> new.beitrag or e.status <> 'sichtbar' then
      raise exception 'WI_ANTWORT';
    end if;
  end if;

  -- Tempo und Mengen (Moderatoren ausgenommen)
  if not public.ist_mod() then
    if exists (select 1 from public.kommentar
               where autor = new.autor
                 and erstellt > now() - make_interval(secs => coalesce(public.einst('abstand_sekunden'), '30')::int)) then
      raise exception 'WI_TEMPO';
    end if;
    select count(*) into n from public.kommentar where autor = new.autor and erstellt > now() - interval '1 hour';
    if n >= coalesce(public.einst('max_pro_stunde'), '15')::int then raise exception 'WI_LIMIT'; end if;
    select count(*) into n from public.kommentar where autor = new.autor and erstellt > now() - interval '1 day';
    if n >= coalesce(public.einst('max_pro_tag'), '60')::int then raise exception 'WI_LIMIT'; end if;
    if exists (select 1 from public.kommentar
               where autor = new.autor and public.normalisiere(text) = public.normalisiere(new.text)
                 and erstellt > now() - interval '1 day') then
      raise exception 'WI_DOPPELT';
    end if;
  end if;

  -- Wortfilter
  select * into f from public.filter_treffer(new.text);
  if f.aktion = 'blocken' then raise exception 'WI_WORT'; end if;
  if f.aktion = 'pruefen' then new.status := 'pruefung'; new.grund := 'Wird kurz geprüft (Wortfilter)'; end if;

  -- Links und neue Nutzer
  if new.status = 'sichtbar' and public.einst('links_pruefen') = 'ja'
     and new.text ~* '(https?://|www\.|\m[a-z0-9-]+\.(de|com|net|org|io|ly|me|to|gg|app|info|xyz)\M)' then
    new.status := 'pruefung'; new.grund := 'Wird kurz geprüft (Link)';
  end if;
  if new.status = 'sichtbar' and public.einst('neue_pruefen') = 'ja' and p.vertrauen = 0 and not public.ist_mod() then
    new.status := 'pruefung'; new.grund := 'Wird kurz geprüft (neues Profil)';
  end if;

  return new;
end $$;

drop trigger if exists wi_kommentar_regeln on public.kommentar;
create trigger wi_kommentar_regeln before insert on public.kommentar
  for each row execute function public.kommentar_regeln();

alter table public.kommentar enable row level security;
drop policy if exists kommentar_lesen on public.kommentar;
create policy kommentar_lesen on public.kommentar for select to anon, authenticated using (
  (status in ('sichtbar', 'geloescht') and not public.ist_schatten(autor))
  or autor = auth.uid()
  or public.ist_mod()
);
drop policy if exists kommentar_schreiben on public.kommentar;
create policy kommentar_schreiben on public.kommentar for insert to authenticated
  with check (autor = auth.uid());

revoke all on public.kommentar from anon, authenticated;
grant select on public.kommentar to anon, authenticated;
grant insert (beitrag, eltern, text) on public.kommentar to authenticated;
-- Kein update/delete direkt: Löschen und Moderieren nur über Funktionen unten.

-- ---------------------------------------------------------------------
-- 5. Likes
-- ---------------------------------------------------------------------
create table if not exists public.kommentar_like (
  kommentar uuid not null references public.kommentar(id) on delete cascade,
  nutzer    uuid not null default auth.uid() references public.profil(id) on delete cascade,
  erstellt  timestamptz not null default now(),
  primary key (kommentar, nutzer)
);
create index if not exists kommentar_like_nutzer_idx on public.kommentar_like (nutzer);

create or replace function public.like_regeln() returns trigger
language plpgsql security definer set search_path = '' as $$
declare k public.kommentar;
begin
  if tg_op = 'INSERT' then
    new.nutzer := auth.uid(); new.erstellt := now();
    if new.nutzer is null then raise exception 'WI_LOGIN'; end if;
    select * into k from public.kommentar where id = new.kommentar;
    if not found or k.status <> 'sichtbar' then raise exception 'WI_WEG'; end if;
    if k.autor = new.nutzer then raise exception 'WI_EIGEN'; end if;
    return new;
  end if;
  return old;
end $$;

create or replace function public.like_zaehlen() returns trigger
language plpgsql security definer set search_path = '' as $$
begin
  if tg_op = 'INSERT' then
    update public.kommentar set likes = likes + 1 where id = new.kommentar;
  else
    update public.kommentar set likes = greatest(likes - 1, 0) where id = old.kommentar;
  end if;
  return null;
end $$;

drop trigger if exists wi_like_regeln on public.kommentar_like;
create trigger wi_like_regeln before insert on public.kommentar_like
  for each row execute function public.like_regeln();
drop trigger if exists wi_like_zaehlen on public.kommentar_like;
create trigger wi_like_zaehlen after insert or delete on public.kommentar_like
  for each row execute function public.like_zaehlen();

alter table public.kommentar_like enable row level security;
drop policy if exists like_eigene_lesen on public.kommentar_like;
create policy like_eigene_lesen on public.kommentar_like for select to authenticated using (nutzer = auth.uid());
drop policy if exists like_setzen on public.kommentar_like;
create policy like_setzen on public.kommentar_like for insert to authenticated with check (nutzer = auth.uid());
drop policy if exists like_entfernen on public.kommentar_like;
create policy like_entfernen on public.kommentar_like for delete to authenticated using (nutzer = auth.uid());
revoke all on public.kommentar_like from anon, authenticated;
grant select, delete on public.kommentar_like to authenticated;
grant insert (kommentar) on public.kommentar_like to authenticated;

-- ---------------------------------------------------------------------
-- 6. Meldungen (Melden-Knopf, Meldeweg nach DSA Art. 16)
-- ---------------------------------------------------------------------
create table if not exists public.kommentar_meldung (
  kommentar uuid not null references public.kommentar(id) on delete cascade,
  nutzer    uuid not null default auth.uid() references public.profil(id) on delete cascade,
  grund     text not null check (grund in ('beleidigung', 'hass', 'spam', 'falschinfo', 'rechtswidrig', 'sonstiges')),
  hinweis   text check (hinweis is null or char_length(hinweis) <= 500),
  erledigt  boolean not null default false,
  erstellt  timestamptz not null default now(),
  primary key (kommentar, nutzer)
);
create index if not exists kommentar_meldung_offen_idx on public.kommentar_meldung (erledigt) where not erledigt;

create or replace function public.meldung_regeln() returns trigger
language plpgsql security definer set search_path = '' as $$
declare k public.kommentar;
begin
  new.nutzer := auth.uid(); new.erledigt := false; new.erstellt := now();
  if new.nutzer is null then raise exception 'WI_LOGIN'; end if;
  select * into k from public.kommentar where id = new.kommentar;
  if not found then raise exception 'WI_WEG'; end if;
  if k.autor = new.nutzer then raise exception 'WI_EIGEN'; end if;
  return new;
end $$;

create or replace function public.meldung_zaehlen() returns trigger
language plpgsql security definer set search_path = '' as $$
declare schwelle int := coalesce(public.einst('meldeschwelle'), '3')::int;
begin
  update public.kommentar
     set meldungen = meldungen + 1,
         status = case when status = 'sichtbar' and (meldungen + 1 >= schwelle or public.ist_mod()) then 'ausgeblendet' else status end,
         grund  = case when status = 'sichtbar' and (meldungen + 1 >= schwelle or public.ist_mod())
                       then 'Ausgeblendet nach Meldungen, wird von der Redaktion geprüft' else grund end
   where id = new.kommentar;
  return null;
end $$;

drop trigger if exists wi_meldung_regeln on public.kommentar_meldung;
create trigger wi_meldung_regeln before insert on public.kommentar_meldung
  for each row execute function public.meldung_regeln();
drop trigger if exists wi_meldung_zaehlen on public.kommentar_meldung;
create trigger wi_meldung_zaehlen after insert on public.kommentar_meldung
  for each row execute function public.meldung_zaehlen();

alter table public.kommentar_meldung enable row level security;
drop policy if exists meldung_senden on public.kommentar_meldung;
create policy meldung_senden on public.kommentar_meldung for insert to authenticated with check (nutzer = auth.uid());
drop policy if exists meldung_eigene on public.kommentar_meldung;
create policy meldung_eigene on public.kommentar_meldung for select to authenticated using (nutzer = auth.uid() or public.ist_mod());
revoke all on public.kommentar_meldung from anon, authenticated;
grant select on public.kommentar_meldung to authenticated;
grant insert (kommentar, grund, hinweis) on public.kommentar_meldung to authenticated;

-- ---------------------------------------------------------------------
-- 7. Protokoll (Nachweis für Moderationsentscheidungen)
-- ---------------------------------------------------------------------
create table if not exists public.moderation_log (
  id       bigint generated always as identity primary key,
  wer      text not null,
  aktion   text not null,
  ziel     text not null,
  grund    text,
  zeit     timestamptz not null default now()
);
alter table public.moderation_log enable row level security;
revoke all on public.moderation_log from anon, authenticated;

create or replace function public.protokoll(a text, z text, g text) returns void
language sql security definer set search_path = '' as $$
  insert into public.moderation_log (wer, aktion, ziel, grund)
  values (coalesce((select name from public.profil where id = auth.uid()), session_user::text), a, z, g)
$$;

-- ---------------------------------------------------------------------
-- 8. Funktionen für Nutzer
-- ---------------------------------------------------------------------
-- Eigenes Profil (inkl. Sperre, damit die Seite den Grund anzeigen kann)
create or replace function public.mein_profil() returns json
language sql stable security definer set search_path = '' as $$
  select json_build_object('id', p.id, 'name', p.name, 'rolle', p.rolle, 'vertrauen', p.vertrauen,
                           'gesperrt_bis', p.gesperrt_bis, 'sperrgrund', p.sperrgrund,
                           'anonym', public.ist_anonym(),
                           'name_gewaehlt', p.name_gewaehlt, 'name_aenderung_frei', p.name_aenderungen < 1, 'verifiziert', p.verifiziert)
  from public.profil p where p.id = auth.uid()
$$;

-- Eigenen Kommentar löschen. Ohne Antworten wird er ganz entfernt,
-- mit Antworten bleibt ein Platzhalter "[gelöscht]" stehen.
create or replace function public.kommentar_loeschen(kid uuid) returns void
language plpgsql security definer set search_path = '' as $$
begin
  if not exists (select 1 from public.kommentar where id = kid and autor = auth.uid()) then raise exception 'WI_WEG'; end if;
  if exists (select 1 from public.kommentar where eltern = kid) then
    update public.kommentar set status = 'geloescht', text = '[gelöscht]', grund = null where id = kid;
  else
    delete from public.kommentar where id = kid;
  end if;
end $$;

-- Zusätzliche Sperrliste nur für Namen (Spielerinnen, NS-Bezüge, Sexuelles).
-- teil = darf nirgends im Namen stecken, exakt = Name darf nicht genau so lauten.
-- Spielerinnen-Namen kommen aus supabase/namenssperre.sql (neu erzeugen, wenn sich Kader ändern).
create table if not exists public.namenssperre (
  wort     text primary key,
  schluessel text generated always as (regexp_replace(public.normalisiere(wort), '[^a-z0-9]', '', 'g')) stored,
  art      text not null default 'teil' check (art in ('teil', 'exakt')),
  info     text
);
alter table public.namenssperre enable row level security;
revoke all on public.namenssperre from anon, authenticated;

insert into public.namenssperre (wort, art, info) values
  ('hitler','teil','NS'), ('adolf','teil','NS'), ('fuehrer','teil','NS'), ('fuhrer','teil','NS'), ('nsdap','teil','NS'),
  ('holocaust','teil','NS'), ('auschwitz','teil','NS'), ('hakenkreuz','teil','NS'), ('swastika','teil','NS'),
  ('1488','teil','NS'), ('reichsbuerger','teil','NS'), ('terror','teil','Gewalt'), ('amok','teil','Gewalt'),
  ('sex','teil','Sexuell'), ('porn','teil','Sexuell'), ('nackt','teil','Sexuell'), ('nude','teil','Sexuell'), ('titten','teil','Sexuell'),
  ('penis','teil','Sexuell'), ('vagina','teil','Sexuell'), ('muschi','teil','Sexuell'), ('schwanz','teil','Sexuell'), ('pussy','teil','Sexuell'),
  ('milf','teil','Sexuell'), ('horny','teil','Sexuell'), ('geil','teil','Sexuell'), ('fetisch','teil','Sexuell'), ('blowjob','teil','Sexuell'),
  ('wichs','teil','Sexuell'), ('hure','teil','Beleidigung'), ('arsch','teil','Beleidigung'), ('paedo','teil','Sexuell'), ('pedophil','teil','Sexuell'),
  ('dfb','exakt','Verwechslung'), ('kickbase','exakt','Verwechslung')
on conflict (wort) do nothing;

-- true, wenn ein Name gegen Filterwörter oder Namenssperre verstößt (Wörter auch zusammengeschrieben, mit Zahlen oder Akzenten)
create or replace function public.name_verboten(n text) returns boolean
language sql stable security definer set search_path = '' as $$
  with k as (select regexp_replace(public.normalisiere(n), '[^a-z0-9]', '', 'g') as key)
  select exists (select 1 from public.filterwort f, k
                 where position(regexp_replace(f.wort_norm, '[^a-z0-9]', '', 'g') in k.key) > 0)
      or exists (select 1 from public.namenssperre s, k
                 where (s.art = 'teil' and position(s.schluessel in k.key) > 0)
                    or (s.art = 'exakt' and s.schluessel = k.key))
$$;

-- Namen festlegen: beim ersten Kommentar frei (auch Platzhalter behalten), danach genau eine Änderung.
-- Gilt für anonyme Profile und Konten gleich. Redaktion ohne Grenze.
create or replace function public.name_aendern(neu text) returns text
language plpgsql security definer set search_path = '' as $$
declare n text := regexp_replace(btrim(coalesce(neu, '')), '\s+', ' ', 'g'); f record; p public.profil;
begin
  if auth.uid() is null then raise exception 'WI_LOGIN'; end if;
  select * into p from public.profil where id = auth.uid();
  if not found then raise exception 'WI_LOGIN'; end if;
  if p.gesperrt_bis is not null and p.gesperrt_bis > now() then raise exception 'WI_GESPERRT'; end if;
  if n = p.name then
    update public.profil set name_gewaehlt = true where id = p.id;   -- Platzhalter behalten zählt als Wahl
    return n;
  end if;
  if p.name_gewaehlt and p.name_aenderungen >= 1 and not public.ist_mod() then raise exception 'WI_NAME_FEST'; end if;
  if n !~ '^[A-Za-z0-9ÄÖÜäöüß][A-Za-z0-9ÄÖÜäöüß _.-]{2,23}$' then raise exception 'WI_NAME'; end if;
  if not public.ist_mod() and (lower(n) ~ '(wosoinsider|woso.?inside|redaktion|admin|moderat|support|offiziell)' or lower(n) ~ '^woso.?fan') then
    raise exception 'WI_NAME';
  end if;
  if public.name_verboten(n) and not public.ist_mod() then raise exception 'WI_NAME'; end if;
  if exists (select 1 from public.profil where lower(name) = lower(n) and id <> p.id) then raise exception 'WI_NAME_VERGEBEN'; end if;
  update public.profil
     set name = n,
         name_aenderungen = case when p.name_gewaehlt then p.name_aenderungen + 1 else p.name_aenderungen end,
         name_gewaehlt = true
   where id = p.id;
  perform public.protokoll('name', p.id::text, p.name || ' -> ' || n);
  return n;
end $$;

-- Anzahl sichtbarer Kommentare je Meldung (für Sprechblasen im Feed)
create or replace function public.kommentar_zahlen(ids text[]) returns table (beitrag text, anzahl bigint)
language sql stable security definer set search_path = '' as $$
  select k.beitrag, count(*) from public.kommentar k
  where k.beitrag = any(ids) and k.status = 'sichtbar' and not public.ist_schatten(k.autor)
  group by k.beitrag
$$;

-- ---------------------------------------------------------------------
-- 9. Funktionen für die Moderation
--    Im SQL Editor (als postgres) oder als Moderator in App/Web nutzbar.
-- ---------------------------------------------------------------------
-- aktion: freigeben | ausblenden | loeschen
create or replace function public.moderieren(kid uuid, aktion text, begruendung text default null) returns void
language plpgsql security definer set search_path = '' as $$
begin
  if not public.darf_moderieren() then raise exception 'WI_KEIN_MOD'; end if;
  if aktion = 'freigeben' then
    update public.kommentar set status = 'sichtbar', grund = null where id = kid;
  elsif aktion = 'ausblenden' then
    update public.kommentar set status = 'ausgeblendet', angeheftet = false,
      grund = coalesce(nullif(btrim(begruendung), ''), 'Verstoß gegen die Kommentarregeln') where id = kid;
  elsif aktion = 'loeschen' then
    delete from public.kommentar where id = kid;
  else
    raise exception 'WI_AKTION';
  end if;
  update public.kommentar_meldung set erledigt = true where kommentar = kid;
  perform public.protokoll(aktion, kid::text, begruendung);
end $$;

-- Anheften: nur sichtbare Hauptkommentare, je Meldung höchstens einer
create or replace function public.anheften(kid uuid, an boolean) returns void
language plpgsql security definer set search_path = '' as $$
declare k public.kommentar;
begin
  if not public.darf_moderieren() then raise exception 'WI_KEIN_MOD'; end if;
  select * into k from public.kommentar where id = kid;
  if not found or k.eltern is not null or k.status <> 'sichtbar' then raise exception 'WI_WEG'; end if;
  if an then update public.kommentar set angeheftet = false where beitrag = k.beitrag and angeheftet; end if;
  update public.kommentar set angeheftet = an where id = kid;
  perform public.protokoll(case when an then 'anheften' else 'loesen' end, kid::text, null);
end $$;

-- Sperren: tage = null bedeutet dauerhaft, tage = 0 hebt die Sperre auf
create or replace function public.nutzer_sperren(uid uuid, tage int, begruendung text default null) returns void
language plpgsql security definer set search_path = '' as $$
begin
  if not public.darf_moderieren() then raise exception 'WI_KEIN_MOD'; end if;
  update public.profil set
    gesperrt_bis = case when tage is null then 'infinity'::timestamptz when tage = 0 then null else now() + make_interval(days => tage) end,
    sperrgrund   = case when tage = 0 then null else coalesce(nullif(btrim(begruendung), ''), 'Verstoß gegen die Kommentarregeln') end
  where id = uid and rolle = 'nutzer';
  perform public.protokoll(case when tage = 0 then 'entsperren' else 'sperren ' || coalesce(tage::text, 'dauerhaft') end, uid::text, begruendung);
end $$;

-- Rollen vergeben (nur Admins): nutzer | moderator | admin. Redaktion bekommt automatisch den Haken.
create or replace function public.rolle_setzen(uid uuid, neu text) returns void
language plpgsql security definer set search_path = '' as $$
begin
  if not (exists (select 1 from public.profil where id = auth.uid() and rolle = 'admin')
          or (auth.uid() is null and session_user in ('postgres', 'supabase_admin'))) then
    raise exception 'WI_KEIN_MOD';
  end if;
  if neu not in ('nutzer', 'moderator', 'admin') then raise exception 'WI_AKTION'; end if;
  if uid = auth.uid() and neu <> 'admin' then raise exception 'WI_AKTION'; end if;  -- sich selbst nicht versehentlich entmachten
  update public.profil set rolle = neu, verifiziert = (neu <> 'nutzer') or verifiziert, vertrauen = greatest(vertrauen, case when neu = 'nutzer' then 0 else 2 end)
   where id = uid;
  perform public.protokoll('rolle ' || neu, uid::text, null);
end $$;

-- Verifiziert-Haken setzen oder entfernen (nur Admins)
create or replace function public.verifizieren(uid uuid, an boolean) returns void
language plpgsql security definer set search_path = '' as $$
begin
  if not (exists (select 1 from public.profil where id = auth.uid() and rolle = 'admin')
          or (auth.uid() is null and session_user in ('postgres', 'supabase_admin'))) then
    raise exception 'WI_KEIN_MOD';
  end if;
  update public.profil set verifiziert = an where id = uid;
  perform public.protokoll(case when an then 'verifiziert' else 'nicht verifiziert' end, uid::text, null);
end $$;

-- Schattensperre: Person sieht ihre Kommentare, sonst niemand
create or replace function public.schattensperre(uid uuid, an boolean) returns void
language plpgsql security definer set search_path = '' as $$
begin
  if not public.darf_moderieren() then raise exception 'WI_KEIN_MOD'; end if;
  update public.profil set schatten = an where id = uid and rolle = 'nutzer';
  perform public.protokoll(case when an then 'schatten an' else 'schatten aus' end, uid::text, null);
end $$;

-- Vertrauensstufe 0 neu, 1 normal, 2 vertraut
create or replace function public.vertrauen_setzen(uid uuid, stufe int) returns void
language plpgsql security definer set search_path = '' as $$
begin
  if not public.darf_moderieren() then raise exception 'WI_KEIN_MOD'; end if;
  update public.profil set vertrauen = stufe where id = uid;
  perform public.protokoll('vertrauen ' || stufe, uid::text, null);
end $$;

-- Warteschlange für eine spätere Moderationsseite in App/Web
create or replace function public.mod_warteschlange() returns setof json
language plpgsql stable security definer set search_path = '' as $$
begin
  if not public.darf_moderieren() then raise exception 'WI_KEIN_MOD'; end if;
  return query
    select json_build_object('id', k.id, 'beitrag', k.beitrag, 'autor', k.autor, 'name', p.name,
             'text', k.text, 'status', k.status, 'grund', k.grund, 'meldungen', k.meldungen,
             'erstellt', k.erstellt,
             'meldegruende', (select json_agg(json_build_object('grund', m.grund, 'hinweis', m.hinweis))
                              from public.kommentar_meldung m where m.kommentar = k.id and not m.erledigt))
    from public.kommentar k join public.profil p on p.id = k.autor
    where k.status in ('pruefung', 'ausgeblendet')
       or exists (select 1 from public.kommentar_meldung m where m.kommentar = k.id and not m.erledigt)
    order by k.erstellt desc
    limit 200;
end $$;

-- ---------------------------------------------------------------------
-- 10. Aufräumen: anonyme Nutzer ohne jede Aktivität nach 30 Tagen löschen
-- ---------------------------------------------------------------------
create or replace function public.aufraeumen() returns int
language plpgsql security definer set search_path = '' as $$
declare n int;
begin
  delete from auth.users u
  where u.is_anonymous
    and u.created_at < now() - interval '30 days'
    and coalesce(u.last_sign_in_at, u.created_at) < now() - interval '30 days'
    and not exists (select 1 from public.kommentar k where k.autor = u.id)
    and not exists (select 1 from public.kommentar_like l where l.nutzer = u.id)
    and not exists (select 1 from public.kommentar_meldung m where m.nutzer = u.id);
  get diagnostics n = row_count;
  -- Erledigte Meldungen nach 6 Monaten, Moderationsprotokoll nach 12 Monaten löschen
  delete from public.kommentar_meldung where erledigt and erstellt < now() - interval '6 months';
  delete from public.moderation_log where zeit < now() - interval '12 months';
  return n;
end $$;

-- ---------------------------------------------------------------------
-- 11. Rechte auf Funktionen
-- ---------------------------------------------------------------------
revoke execute on all functions in schema public from public, anon;
-- Für alle (auch ohne Anmeldung)
grant execute on function public.kommentar_zahlen(text[]) to anon, authenticated;
-- Hilfsfunktionen, die in Regeln (RLS) für Leser gebraucht werden
grant execute on function public.ist_mod(), public.ist_schatten(uuid), public.ist_anonym(), public.einst(text) to anon, authenticated;
-- Nur mit Sitzung
grant execute on function public.mein_profil(), public.kommentar_loeschen(uuid), public.name_aendern(text),
  public.moderieren(uuid, text, text), public.nutzer_sperren(uuid, int, text), public.schattensperre(uuid, boolean),
  public.vertrauen_setzen(uuid, int), public.mod_warteschlange(), public.anheften(uuid, boolean), public.rolle_setzen(uuid, text), public.verifizieren(uuid, boolean) to authenticated;
-- Intern (Trigger, Filter, Aufräumen): nicht von außen aufrufbar
revoke execute on function public.profil_anlegen(), public.kommentar_regeln(), public.like_regeln(), public.like_zaehlen(),
  public.meldung_regeln(), public.meldung_zaehlen(), public.filter_treffer(text), public.protokoll(text, text, text),
  public.aufraeumen(), public.darf_moderieren(), public.name_verboten(text) from authenticated;

commit;

-- =====================================================================
-- Optional, einzeln ausführen (nicht Teil des Laufs oben)
-- =====================================================================
-- Aufräumen täglich um 03:17 (Database > Extensions > pg_cron vorher aktivieren):
--   select cron.schedule('wi-aufraeumen', '17 3 * * *', 'select public.aufraeumen()');
--
-- Weitere Admins/Moderatoren bestimmen (Name aus den Kommentaren):
--   select public.rolle_setzen((select id from public.profil where name = 'Lena aus Köln'), 'moderator');
--   select public.verifizieren((select id from public.profil where name = 'FC Bayern Frauen'), true);
--
-- Eigenes Gerät zum Redaktions-Profil machen (ID steht in der Tabelle profil,
-- schreib einen Kommentar und nutze den Namen, den du dabei gewählt hast):
--   update public.profil set rolle = 'admin', name = 'WOSOINSIDER Redaktion' where name = '<dein Name>';
--
-- Moderation im SQL Editor:
--   select * from public.mod_warteschlange();
--   select public.moderieren('<kommentar-id>', 'ausblenden', 'Beleidigung');
--   select public.moderieren('<kommentar-id>', 'freigeben');
--   select public.nutzer_sperren('<nutzer-id>', 7, 'Wiederholte Beleidigungen');   -- 7 Tage
--   select public.nutzer_sperren('<nutzer-id>', null, 'Spam');                      -- dauerhaft
--   update public.einstellung set wert = 'nein' where schluessel = 'kommentare_an'; -- Notschalter
--   insert into public.filterwort (wort, aktion) values ('beispiel', 'blocken');
