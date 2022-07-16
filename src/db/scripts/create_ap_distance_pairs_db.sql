create table if not exists airport_distance_mapping
(
    id          serial
        constraint airport_distance_mapping_pk
            primary key,
    pairID      varchar(7)     unique not null,
    ap1         varchar(3)     not null,
    ap2         varchar(3)     not null,
    distance_km double precision not null
);

create index if not exists airport_distance_mapping_pairID_index
    on airport_distance_mapping (pairID);

create index if not exists airport_distance_mapping_ap1_index
    on airport_distance_mapping (ap1);

create index if not exists airport_distance_mapping_ap2_index
    on airport_distance_mapping (ap2);

