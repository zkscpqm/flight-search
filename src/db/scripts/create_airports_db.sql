create table if not exists airports
(
    uid          varchar(20)
                 constraint airports_pk
                 primary key,

    full_name    varchar(150)     not null,
    iso_country  varchar(8),
    iso_region   varchar(16),
    municipality varchar(50),
    latitude     double precision not null,
    longitude    double precision not null,
    size         varchar(16)      not null,
    iata_code    varchar(8)       not null,
    local_code   varchar(16)
);

create index if not exists airports_iata_code_index
    on airports (iata_code desc);

create index if not exists airports_uid_index
    on airports (uid desc);
