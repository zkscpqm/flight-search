create table if not exists airport_distance_mapping
(
    pair_id     varchar(60)
                constraint airport_distance_mapping_pk
                primary key,
    ap1         varchar(30)      not null,
    ap2         varchar(30)      not null,
    distance_km double precision not null
);

create index if not exists airport_distance_mapping_ap1_ap2_index
    on airport_distance_mapping (ap1 desc, ap2 desc);

create index if not exists airport_distance_mapping_ap2_index
    on airport_distance_mapping (ap2 desc);

create index if not exists airport_distance_mapping_pair_id_index
    on airport_distance_mapping (pair_id desc);
