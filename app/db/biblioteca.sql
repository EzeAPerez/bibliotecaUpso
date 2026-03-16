CREATE DATABASE bibliotecaUpso CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

------------ sedes -------------
/*
    Tabla con los datos de las distintas sedes. 
    id --> SMALLINT UNSIGNED AUTO_INCREMENT / identificador unico de la sede.
    nombre --> VARCHAR(50) / nombre de la ciudad donde se encuentra la sede. 

    A la hora de incorporar nuevas sedes, no puede existir una sede con mismo nombres. 
*/

CREATE TABLE sedes (
    id SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    CONSTRAINT uq_sedes_nombre UNIQUE (nombre)
);



INSERT INTO sedes (nombre) VALUES ('Bahia Blanca') ;
INSERT INTO sedes (nombre) VALUES ('Carhué') ;
INSERT INTO sedes (nombre) VALUES ('Carmen de Patagones') ;
INSERT INTO sedes (nombre) VALUES ('Casbas') ;
INSERT INTO sedes (nombre) VALUES ('Coronel Dorrego') ;
INSERT INTO sedes (nombre) VALUES ('Coronel Pringles') ;
INSERT INTO sedes (nombre) VALUES ('Coronel Suarez') ;
INSERT INTO sedes (nombre) VALUES ('Daireaux') ;
INSERT INTO sedes (nombre) VALUES ('Darregueira') ;
INSERT INTO sedes (nombre) VALUES ('General La Madrid') ;
INSERT INTO sedes (nombre) VALUES ('Hilario Ascasubi') ;
INSERT INTO sedes (nombre) VALUES ('Laprida') ;
INSERT INTO sedes (nombre) VALUES ('Medanos') ;
INSERT INTO sedes (nombre) VALUES ('Monte Hermoso') ;
INSERT INTO sedes (nombre) VALUES ('Pedro Luro') ;
INSERT INTO sedes (nombre) VALUES ('Pelegrini') ;
INSERT INTO sedes (nombre) VALUES ('Pigüé') ;
INSERT INTO sedes (nombre) VALUES ('Puan') ;
INSERT INTO sedes (nombre) VALUES ('Punta Alta') ;
INSERT INTO sedes (nombre) VALUES ('Saavedra') ;
INSERT INTO sedes (nombre) VALUES ('Saldungaray') ;
INSERT INTO sedes (nombre) VALUES ('Salliqueló') ;
INSERT INTO sedes (nombre) VALUES ('Tres Arroyos') ;
INSERT INTO sedes (nombre) VALUES ('Tres Lomas') ;
INSERT INTO sedes (nombre) VALUES ('Villalonga') ;

------------ tipo_material ------------
/*
    Tabla con los tipos de obras. 
    id --> SMALLINT UNSIGNED AUTO_INCREMENT / identificador unico de la sede.
    tipo --> VARCHAR(50) / nombre del tipo de obra.

    A la hora de incorporar nuevos tipos de obras, no puede existir un tipo con mismo nombre. 
*/
CREATE TABLE tipo_material (
    id SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    CONSTRAINT uq_tipo_material_tipo UNIQUE (tipo)
);

INSERT INTO tipo_material (tipo) VALUES ('Libro');
INSERT INTO tipo_material (tipo) VALUES ('Revista');
INSERT INTO tipo_material (tipo) VALUES ('Tesis');
INSERT INTO tipo_material (tipo) VALUES ('Otros');

------------ estado_obra -------------
/*
    Tabla con los estados de un obra. 
    En el se almacena los distintos estados que puede pasar una obra.
    DISPONIBLE: determina que obra esta disponible en su ubicacion y listo para ser reservado.
    RESERVADO: determina que obra fue reservado por un usario y esta esperando por ser retidado o en viaje.
    PRESTADO: el usuario que reservo la obra, retiro y esta en su posecion.
    VENCIDO: la obra no fue devuelta en el plazo acordado y no se encuentra disponible.
    DE_BAJA: por cuestiones de administracion la obra fue dada de baja de forma manual. 
*/
CREATE TABLE estado_obra (
    id SMALLINT UNSIGNED PRIMARY KEY,
    estado VARCHAR(50) NOT NULL,
    CONSTRAINT uq_estado_obra_estado UNIQUE (estado)
);

INSERT INTO estado_obra (id, estado) VALUES 
(1, 'DISPONIBLE'), 
(2, 'RESERVADO'), 
(3, 'PRESTADO'), 
(4, 'VENCIDO'),
(5, 'DE_BAJA');


CREATE TABLE area_tematica (
    id SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    CONSTRAINT uq_area_tematica_nombre UNIQUE (nombre)
);

INSERT INTO area_tematica (nombre) values ('Administracion');
INSERT INTO area_tematica (nombre) values ('Administracion de Empresas Agropecuarias');
INSERT INTO area_tematica (nombre) values ('Agronomia');
INSERT INTO area_tematica (nombre) values ('Audiovisuales');
INSERT INTO area_tematica (nombre) values ('Ciencias Sociales');
INSERT INTO area_tematica (nombre) values ('Comercio Exterior');
INSERT INTO area_tematica (nombre) values ('Contabilidad');
INSERT INTO area_tematica (nombre) values ('Deporte');
INSERT INTO area_tematica (nombre) values ('Derecho');
INSERT INTO area_tematica (nombre) values ('Desarrollo Local y Regional');
INSERT INTO area_tematica (nombre) values ('Diseño');
INSERT INTO area_tematica (nombre) values ('Economia');
INSERT INTO area_tematica (nombre) values ('Emprendedorismo');
INSERT INTO area_tematica (nombre) values ('Fisica');
INSERT INTO area_tematica (nombre) values ('Geografia');
INSERT INTO area_tematica (nombre) values ('Historia');
INSERT INTO area_tematica (nombre) values ('Idioma');
INSERT INTO area_tematica (nombre) values ('Informatica');
INSERT INTO area_tematica (nombre) values ('Ingenieria');
INSERT INTO area_tematica (nombre) values ('Matematica');
INSERT INTO area_tematica (nombre) values ('Periodismo');
INSERT INTO area_tematica (nombre) values ('Quimica');
INSERT INTO area_tematica (nombre) values ('Salud');
INSERT INTO area_tematica (nombre) values ('Turismo');


CREATE TABLE subarea_tematica(
    id SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    id_area_tematica SMALLINT UNSIGNED NOT NULL,
    FOREIGN KEY (id_area_tematica) REFERENCES area_tematica(id),
    CONSTRAINT uq_subarea_tematica_nombre_area UNIQUE (nombre, id_area_tematica)
);
INSERT INTO subarea_tematica (nombre, id_area_tematica) values ('Sociologia', 1);

CREATE TABLE obra_subarea_tematica (
    id_obra MEDIUMINT UNSIGNED NOT NULL,
    id_subarea SMALLINT UNSIGNED NOT NULL,
    PRIMARY KEY (id_obra, id_subarea),
    FOREIGN KEY (id_obra) REFERENCES obras(id),
    FOREIGN KEY (id_subarea) REFERENCES subarea_tematica(id)
);

------------ Materiales / Obras -------------
CREATE TABLE obras(
    id MEDIUMINT UNSIGNED AUTO_INCREMENT PRIMARY KEY, 
    id_tipo_material SMALLINT UNSIGNED NOT NULL,
    codigo_fisico VARCHAR(25) NOT NULL, 
    titulo VARCHAR(255) NOT NULL,
    subtitulo VARCHAR(255),
    formato VARCHAR(50),
    anio SMALLINT UNSIGNED,
    autor VARCHAR(255),
    ubicacion_fisica VARCHAR(255),
    anio_ingreso SMALLINT UNSIGNED,
    tipo_de_ingreso VARCHAR(100),
    id_sede SMALLINT UNSIGNED NOT NULL,
    id_estado SMALLINT UNSIGNED NOT NULL DEFAULT 1,

    isbn VARCHAR(20),
    edicion VARCHAR(100),
    editorial VARCHAR(100),
    tomo VARCHAR(100),

    issn VARCHAR(20),
    volumen VARCHAR(100),
    numero VARCHAR(100),

    institucion VARCHAR(255),
    nivel_academico VARCHAR(150),

    FOREIGN KEY (id_tipo_material) REFERENCES tipo_material(id),
    FOREIGN KEY (id_sede) REFERENCES sedes(id),
    FOREIGN KEY (id_estado) REFERENCES estado_obra(id),
    CONSTRAINT uq_libros_codigo UNIQUE (codigo_fisico)
);