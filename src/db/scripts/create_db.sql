create table airport_distance_mapping
(
    id          serial
        constraint airport_distance_mapping_pk
            primary key,
    ap1         varchar(256)     not null,
    ap2         varchar(256)     not null,
    distance_km double precision not null
);

create index airport_distance_mapping_ap1_index
    on airport_distance_mapping (ap1);

create index airport_distance_mapping_ap2_index
    on airport_distance_mapping (ap2);

