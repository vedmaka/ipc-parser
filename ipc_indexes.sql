CREATE TABLE ipc_indexes (
  id int(11) NOT NULL AUTO_INCREMENT,
  level int(11) DEFAULT NULL,
  word varchar(255) DEFAULT NULL,
  category varchar(512) DEFAULT NULL,
  code varchar(255) DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE INDEX UK_ipc_indexes_code (code),
  UNIQUE INDEX UK_ipc_indexes_word (word)
)
ENGINE = INNODB
AUTO_INCREMENT = 1
CHARACTER SET utf8
COLLATE utf8_general_ci;