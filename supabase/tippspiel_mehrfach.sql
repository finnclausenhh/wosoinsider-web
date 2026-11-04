-- Nachtrag 04.11.2026: mehrere richtige Antworten (Komma) in der Wertung. Einmal im Supabase SQL Editor ausführen.
-- Rangliste eines Spieltags (p_md) oder der Saison (p_md = null): Name aus den Kommentar-Profilen
create or replace function public.tipp_rangliste(p_md int default null, p_anzahl int default 50) returns jsonb
language sql stable security definer set search_path = '' as $$
  with pkt as (
    select t.nutzer, sum(case when t.antwort = any(string_to_array(l.antwort, ',')) then 10 else 0 end) as punkte,
           count(*) filter (where t.antwort = any(string_to_array(l.antwort, ','))) as richtig, count(*) as gewertet
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

