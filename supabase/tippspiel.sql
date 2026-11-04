-- =====================================================================
-- WOSOINSIDER: Tippspiel "Spielt sie?" (Supabase / Postgres)
-- Stand 04.11.2026
--
-- Einmal komplett im Supabase SQL Editor ausführen ("Run"), NACH kommentare.sql.
-- Darf erneut ausgeführt werden: Tabellen bleiben, Funktionen und Regeln werden aktualisiert.
--
-- Prinzip (Entscheidung Finn 04.11.2026)
-- * Tippen mit derselben anonymen Sitzung wie die Kommentare, ohne Konto.
-- * Tipps lassen sich bis zum Tippschluss ändern, gewertet wird der letzte Stand.
-- * Tippschluss = 90 Minuten vor dem ersten Ligaanstoß des Spieltags. Die Datenbank
--   holt die Anstoßzeiten selbst aus spielplan.json (alle 30 Minuten), die Seite kann
--   den Schluss also nicht verschieben.
-- * Zwischenstand der Fans: nur für Fragen, die man selbst schon getippt hat, nach dem
--   Tippschluss für alle.
-- * Verlauf: jede Stunde ein Schnappschuss je Frage und Antwort (für die Verlaufskurve).
-- * Wertung: tipp_loesung wird aus tipp_loesung.json (Repo fbl-daten) übernommen,
--   sobald die offiziellen Aufstellungen da sind. 10 Punkte je richtige Antwort.
-- * Lesen der eigenen Tipps nur für sich selbst. Fremde Tipps sieht niemand einzeln.
--
-- Voraussetzungen im Dashboard (Database > Extensions): pg_cron und http einschalten.
-- =====================================================================

begin;

create extension if not exists http with schema extensions;
create extension if not exists pg_cron;

insert into public.einstellung (schluessel, wert, info) values
  ('tippspiel_an',     'ja',  'Notschalter. nein = niemand kann tippen, Lesen geht weiter'),
  ('tipp_schluss_min', '90',  'Tippschluss so viele Minuten vor dem ersten Ligaanstoß des Spieltags'),
  ('tipp_daten_url',   'https://finnclausenhh.github.io/fbl-daten/', 'Basisadresse für spielplan.json und tipp_loesung.json')
on conflict (schluessel) do nothing;

-- ---------------------------------------------------------------------
-- 1. Runden (Spieltag, Tippschluss) aus spielplan.json
-- ---------------------------------------------------------------------
create table if not exists public.tipp_runde (
  md            int primary key,
  erster_anstoss timestamptz not null,
  schluss       timestamptz not null,
  aktualisiert  timestamptz not null default now()
);
alter table public.tipp_runde enable row level security;
drop policy if exists tipp_runde_lesen on public.tipp_runde;
create policy tipp_runde_lesen on public.tipp_runde for select to anon, authenticated using (true);
revoke all on public.tipp_runde from anon, authenticated;
grant select on public.tipp_runde to anon, authenticated;

create or replace function public.tipp_runden_laden() returns int
language plpgsql security definer set search_path = '' as $$
declare
  antwort extensions.http_response;
  plan jsonb;
  n int := 0;
begin
  select * into antwort from extensions.http_get(public.einst('tipp_daten_url') || 'spielplan.json');
  if antwort.status <> 200 then raise warning 'spielplan.json: HTTP %', antwort.status; return 0; end if;
  plan := antwort.content::jsonb;
  with anst as (
    select (t->>'nr')::int as md,
           min(((p->>'anstoss')::timestamp) at time zone 'Europe/Berlin') as erst
    from jsonb_array_elements(plan->'spieltage') t,
         jsonb_array_elements(t->'partien') p
    where p->>'anstoss' ~ '^\d{4}-\d\d-\d\dT\d\d:\d\d'
      and p->>'anstoss' not like '%T00:00%'
      and coalesce(p->>'wettbewerb', '') in ('', 'Liga')
    group by 1
  )
  insert into public.tipp_runde (md, erster_anstoss, schluss, aktualisiert)
  select md, erst, erst - make_interval(mins => public.einst('tipp_schluss_min')::int), now() from anst
  on conflict (md) do update
    set erster_anstoss = excluded.erster_anstoss, schluss = excluded.schluss, aktualisiert = now();
  get diagnostics n = row_count;
  return n;
end $$;
revoke all on function public.tipp_runden_laden() from public, anon, authenticated;

-- ---------------------------------------------------------------------
-- 2. Tipps (eine Antwort je Nutzer, Spieltag und Frage)
-- ---------------------------------------------------------------------
create table if not exists public.tipp (
  nutzer    uuid not null default auth.uid() references auth.users(id) on delete cascade,
  md        int  not null,
  frage     text not null check (char_length(frage) between 1 and 80),
  antwort   text not null check (char_length(antwort) between 1 and 80),
  erstellt  timestamptz not null default now(),
  geaendert timestamptz not null default now(),
  primary key (nutzer, md, frage)
);
create index if not exists tipp_md_frage on public.tipp (md, frage);
alter table public.tipp enable row level security;
drop policy if exists tipp_eigene on public.tipp;
create policy tipp_eigene on public.tipp for select to authenticated using (nutzer = auth.uid());
revoke all on public.tipp from anon, authenticated;
grant select on public.tipp to authenticated;

-- Tipp setzen, ändern oder zurücknehmen (antwort = null). Nur vor dem Tippschluss.
create or replace function public.tipp_setzen(p_md int, p_frage text, p_antwort text) returns jsonb
language plpgsql security definer set search_path = '' as $$
declare
  r public.tipp_runde;
  n int;
begin
  if auth.uid() is null then raise exception 'Keine Sitzung'; end if;
  if coalesce(public.einst('tippspiel_an'), 'ja') <> 'ja' then raise exception 'Tippspiel pausiert'; end if;
  select * into r from public.tipp_runde where md = p_md;
  if r.md is null then raise exception 'Spieltag % unbekannt', p_md; end if;
  if now() >= r.schluss then raise exception 'Tippschluss vorbei'; end if;
  -- Tempo: höchstens 60 Änderungen pro Minute und Nutzer
  select count(*) into n from public.tipp where nutzer = auth.uid() and geaendert > now() - interval '1 minute';
  if n > 60 then raise exception 'Zu viele Änderungen, bitte kurz warten'; end if;
  if p_antwort is null then
    delete from public.tipp where nutzer = auth.uid() and md = p_md and frage = p_frage;
  else
    insert into public.tipp (nutzer, md, frage, antwort) values (auth.uid(), p_md, p_frage, p_antwort)
    on conflict (nutzer, md, frage) do update set antwort = excluded.antwort, geaendert = now();
  end if;
  return public.tipp_stand(p_md);
end $$;
revoke all on function public.tipp_setzen(int, text, text) from public, anon;
grant execute on function public.tipp_setzen(int, text, text) to authenticated;

-- Eigene Tipps eines Spieltags: {"frage": "antwort", ...}
create or replace function public.meine_tipps(p_md int) returns jsonb
language sql stable security definer set search_path = '' as $$
  select coalesce(jsonb_object_agg(frage, antwort), '{}'::jsonb)
  from public.tipp where nutzer = auth.uid() and md = p_md
$$;
revoke all on function public.meine_tipps(int) from public, anon;
grant execute on function public.meine_tipps(int) to authenticated;

-- Zwischenstand: {"frage": {"antwort": anzahl, ...}, ...}
-- Vor dem Tippschluss nur für Fragen, die man selbst getippt hat.
create or replace function public.tipp_stand(p_md int) returns jsonb
language sql stable security definer set search_path = '' as $$
  with r as (select schluss from public.tipp_runde where md = p_md),
  sichtbar as (
    select distinct t.frage from public.tipp t
    where t.md = p_md and ((select now() >= schluss from r) or exists (
      select 1 from public.tipp m where m.nutzer = auth.uid() and m.md = p_md and m.frage = t.frage))
  ),
  z as (
    select t.frage, t.antwort, count(*) as n
    from public.tipp t join sichtbar s on s.frage = t.frage
    where t.md = p_md group by 1, 2
  )
  select coalesce(jsonb_object_agg(frage, a), '{}'::jsonb)
  from (select frage, jsonb_object_agg(antwort, n) as a from z group by frage) x
$$;
revoke all on function public.tipp_stand(int) from public;
grant execute on function public.tipp_stand(int) to anon, authenticated;

-- ---------------------------------------------------------------------
-- 3. Verlauf (stündlicher Schnappschuss)
-- ---------------------------------------------------------------------
create table if not exists public.tipp_verlauf (
  md      int  not null,
  frage   text not null,
  antwort text not null,
  zeit    timestamptz not null,
  anzahl  int  not null,
  primary key (md, frage, antwort, zeit)
);
alter table public.tipp_verlauf enable row level security;
revoke all on public.tipp_verlauf from anon, authenticated;

create or replace function public.tipp_verlauf_sichern() returns int
language plpgsql security definer set search_path = '' as $$
declare n int;
begin
  insert into public.tipp_verlauf (md, frage, antwort, zeit, anzahl)
  select t.md, t.frage, t.antwort, date_trunc('hour', now()), count(*)
  from public.tipp t join public.tipp_runde r on r.md = t.md
  where now() < r.schluss + interval '1 hour'
  group by 1, 2, 3
  on conflict (md, frage, antwort, zeit) do update set anzahl = excluded.anzahl;
  get diagnostics n = row_count;
  return n;
end $$;
revoke all on function public.tipp_verlauf_sichern() from public, anon, authenticated;

-- Verlauf einer Frage: [{"zeit": ..., "antwort": ..., "anzahl": ...}], gleiche Sichtbarkeit wie tipp_stand
create or replace function public.tipp_verlauf(p_md int, p_frage text) returns jsonb
language sql stable security definer set search_path = '' as $$
  select coalesce(jsonb_agg(jsonb_build_object('zeit', v.zeit, 'antwort', v.antwort, 'anzahl', v.anzahl) order by v.zeit), '[]'::jsonb)
  from public.tipp_verlauf v
  where v.md = p_md and v.frage = p_frage
    and ((select now() >= schluss from public.tipp_runde where md = p_md)
         or exists (select 1 from public.tipp m where m.nutzer = auth.uid() and m.md = p_md and m.frage = p_frage))
$$;
revoke all on function public.tipp_verlauf(int, text) from public;
grant execute on function public.tipp_verlauf(int, text) to anon, authenticated;

-- ---------------------------------------------------------------------
-- 4. Wertung und Rangliste
-- ---------------------------------------------------------------------
create table if not exists public.tipp_loesung (
  md      int  not null,
  frage   text not null,
  antwort text not null,
  primary key (md, frage)
);
alter table public.tipp_loesung enable row level security;
drop policy if exists tipp_loesung_lesen on public.tipp_loesung;
create policy tipp_loesung_lesen on public.tipp_loesung for select to anon, authenticated using (true);
revoke all on public.tipp_loesung from anon, authenticated;
grant select on public.tipp_loesung to anon, authenticated;

-- tipp_loesung.json: {"md": 9, "loesung": {"frage-id": "antwort-id", ...}} (fehlt die Datei, passiert nichts)
create or replace function public.tipp_loesung_laden() returns int
language plpgsql security definer set search_path = '' as $$
declare antwort extensions.http_response; d jsonb; n int := 0;
begin
  select * into antwort from extensions.http_get(public.einst('tipp_daten_url') || 'tipp_loesung.json');
  if antwort.status <> 200 then return 0; end if;
  d := antwort.content::jsonb;
  insert into public.tipp_loesung (md, frage, antwort)
  select (d->>'md')::int, key, value from jsonb_each_text(d->'loesung')
  on conflict (md, frage) do update set antwort = excluded.antwort;
  get diagnostics n = row_count;
  return n;
end $$;
revoke all on function public.tipp_loesung_laden() from public, anon, authenticated;

-- Rangliste eines Spieltags (p_md) oder der Saison (p_md = null): Name aus den Kommentar-Profilen
create or replace function public.tipp_rangliste(p_md int default null, p_anzahl int default 50) returns jsonb
language sql stable security definer set search_path = '' as $$
  with pkt as (
    select t.nutzer, sum(case when t.antwort = l.antwort then 10 else 0 end) as punkte,
           count(*) filter (where t.antwort = l.antwort) as richtig, count(*) as gewertet
    from public.tipp t join public.tipp_loesung l on l.md = t.md and l.frage = t.frage
    where p_md is null or t.md = p_md
    group by t.nutzer
  ),
  rang as (
    select p.*, rank() over (order by punkte desc) as platz from pkt p
  )
  select jsonb_build_object(
    'liste', coalesce((select jsonb_agg(jsonb_build_object('platz', r.platz, 'name', coalesce(pr.name, 'Fan'), 'punkte', r.punkte,
                  'richtig', r.richtig, 'gewertet', r.gewertet, 'ich', r.nutzer = auth.uid()) order by r.platz, pr.name)
               from (select * from rang order by platz limit greatest(1, least(p_anzahl, 200))) r
               left join public.profil pr on pr.id = r.nutzer), '[]'::jsonb),
    'ich', (select jsonb_build_object('platz', platz, 'punkte', punkte, 'richtig', richtig, 'gewertet', gewertet)
            from rang where nutzer = auth.uid()),
    'teilnehmer', (select count(*) from rang))
$$;
revoke all on function public.tipp_rangliste(int, int) from public;
grant execute on function public.tipp_rangliste(int, int) to anon, authenticated;

commit;

-- ---------------------------------------------------------------------
-- 5. Zeitpläne (pg_cron). Außerhalb der Transaktion, darf erneut laufen.
-- ---------------------------------------------------------------------
select cron.unschedule(jobid) from cron.job where jobname in ('tipp_runden', 'tipp_verlauf', 'tipp_loesung');
select cron.schedule('tipp_runden',  '*/30 * * * *', $$select public.tipp_runden_laden()$$);
select cron.schedule('tipp_verlauf', '5 * * * *',    $$select public.tipp_verlauf_sichern()$$);
select cron.schedule('tipp_loesung', '*/15 * * * *', $$select public.tipp_loesung_laden()$$);
-- Sofort einmal laden, damit der aktuelle Spieltag da ist:
select public.tipp_runden_laden();
