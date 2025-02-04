-- お題を取得する関数
-- view_count が最小で、かつ created_at が最も古いお題を取得し、view_count をインクリメントする
create or replace function get_odai()
returns table(id uuid, text text, created_at timestamp, view_count int)
language sql
as $$
  with selected as (
    select * from odai
    order by view_count asc, created_at asc
    limit 1
  ), updated as (
    update odai
    set view_count = view_count + 1
    where id = (select id from selected)
    returning *
  )
  select * from updated;
$$;
