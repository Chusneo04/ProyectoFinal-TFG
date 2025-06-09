use bpecpur5dhkqodh6mbal;

/*

create table usuarios(
	id int not null auto_increment primary key,
    nombre varchar(30) not null,
    apellidos varchar(80) not null,
    correo varchar(100) not null,
    clave varchar(255) not null,
    fecha_de_creacion date not null,
    token varchar(70),
    imagen varchar(255)
);

create table curriculums(
	id_curriculum int not null auto_increment primary key,
    id_usuario int not null,
    plantilla int not null,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE
);

create table experiencia(
	id_experiencia int not null auto_increment primary key,
    id_curriculum int not null,
    fechas varchar(70) not null,
    puesto varchar(120) not null,
    labor_1 varchar(255) not null,
    labor_2 varchar(255) not null,
    labor_3 varchar(255) not null,
    FOREIGN KEY (id_curriculum) REFERENCES curriculums(id_curriculum) ON DELETE CASCADE
);

create table formacion(
	id_formacion int not null auto_increment primary key,
    id_curriculum int not null,
    año varchar(8) not null,
    titulo varchar(120) not null,
    temas varchar(255) not null,
    FOREIGN KEY (id_curriculum) REFERENCES curriculums(id_curriculum) ON DELETE CASCADE
);


create table datos(
	id_datos int not null auto_increment primary key,
    id_curriculum int not null,
    direccion varchar(120) not null,
    telefono varchar(9) not null,
    resumen_profesional varchar(255) not null,
    aptitud_1 varchar(50) not null,
    aptitud_2 varchar(50) not null,
    aptitud_3 varchar(50) not null,
    aptitud_4 varchar(50),
    aptitud_5 varchar(50),
    FOREIGN KEY (id_curriculum) REFERENCES curriculums(id_curriculum) ON DELETE CASCADE
);

*/

select * from usuarios;