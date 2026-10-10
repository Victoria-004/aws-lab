-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: lab3_db
-- ------------------------------------------------------
-- Server version	8.0.43

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `callparticipation`
--

DROP TABLE IF EXISTS `callparticipation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `callparticipation` (
  `call_participation_id` int NOT NULL AUTO_INCREMENT,
  `call_id` int NOT NULL,
  `rescuers_id` int NOT NULL,
  `vehicle_id` int NOT NULL,
  `departure_time` datetime DEFAULT NULL,
  `return_time` datetime DEFAULT NULL,
  PRIMARY KEY (`call_participation_id`),
  KEY `fk_call_callparticipation` (`call_id`),
  KEY `fk_call_rescuers` (`rescuers_id`),
  KEY `fk_call_vehicle` (`vehicle_id`),
  CONSTRAINT `fk_call_callparticipation` FOREIGN KEY (`call_id`) REFERENCES `calls` (`call_id`),
  CONSTRAINT `fk_call_rescuers` FOREIGN KEY (`rescuers_id`) REFERENCES `rescuers` (`rescuers_id`),
  CONSTRAINT `fk_call_vehicle` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`vehicle_id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `callparticipation`
--

LOCK TABLES `callparticipation` WRITE;
/*!40000 ALTER TABLE `callparticipation` DISABLE KEYS */;
INSERT INTO `callparticipation` VALUES (1,1,4,3,'2025-09-24 14:05:00','2025-09-24 14:45:00'),(2,1,3,3,'2025-09-24 14:05:00','2025-09-24 14:45:00'),(3,2,14,1,'2025-09-24 15:35:00','2025-09-24 16:20:00'),(4,2,3,4,'2025-09-24 15:35:00','2025-09-24 16:20:00'),(5,3,2,1,'2025-09-24 16:50:00','2025-09-24 17:30:00'),(6,4,1,1,'2025-09-25 09:15:00','2025-09-25 09:40:00'),(7,5,5,5,'2025-09-26 11:05:00','2025-09-26 13:00:00'),(8,5,15,6,'2025-09-26 11:05:00','2025-09-26 13:00:00'),(9,5,6,5,'2025-09-26 11:05:00','2025-09-26 13:00:00'),(10,5,10,6,'2025-09-26 11:05:00','2025-09-26 13:00:00'),(11,6,6,7,'2025-09-26 14:35:00','2025-09-26 15:45:00'),(12,7,7,9,'2025-09-27 08:05:00','2025-09-27 09:15:00'),(13,8,8,13,'2025-09-28 19:05:00','2025-09-28 19:40:00'),(14,9,9,12,'2025-09-29 21:05:00','2025-09-29 22:30:00'),(15,10,12,15,'2025-10-01 07:05:00','2025-10-01 08:30:00'),(16,11,3,3,'2025-10-01 10:35:00','2025-10-01 11:45:00'),(17,11,14,1,'2025-10-01 10:35:00','2025-10-01 11:45:00'),(18,11,1,2,'2025-10-01 10:35:00','2025-10-01 11:45:00'),(19,12,13,1,'2025-10-02 12:05:00','2025-10-02 12:45:00'),(20,15,7,9,'2025-10-15 22:05:00','2025-10-15 23:30:00');
/*!40000 ALTER TABLE `callparticipation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `calls`
--

DROP TABLE IF EXISTS `calls`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `calls` (
  `call_id` int NOT NULL AUTO_INCREMENT,
  `emergency_type_id` int NOT NULL,
  `caller_phone` varchar(45) COLLATE utf8mb4_unicode_ci NOT NULL,
  `caller_name` varchar(45) COLLATE utf8mb4_unicode_ci NOT NULL,
  `short_description` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `full_description` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `adress` varchar(45) COLLATE utf8mb4_unicode_ci NOT NULL,
  `cause_description` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `call_date` date NOT NULL,
  `call_time` time NOT NULL,
  PRIMARY KEY (`call_id`),
  KEY `fk_call_emergency_type` (`emergency_type_id`),
  CONSTRAINT `fk_call_emergency_type` FOREIGN KEY (`emergency_type_id`) REFERENCES `emergencytypes` (`emergency_type_id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `calls`
--

LOCK TABLES `calls` WRITE;
/*!40000 ALTER TABLE `calls` DISABLE KEYS */;
INSERT INTO `calls` VALUES (1,1,'0971234567','Анна','Пожежа в квартирі','Пожежа на 4-му поверсі житлового будинку.','вул. Городоцька, 20','Необережність','2025-09-24','14:00:00'),(2,2,'0679876543','Олег','ДТП на кільцевій','Стовпове зіткнення, є постраждалі.','Кільцева дорога, 15','Перевищення швидкості','2025-09-24','15:30:00'),(3,3,'0501112233','Сергій','Затоплення підвалу','Вода піднімається у житловому будинку.','вул. Симоненка, 30','Аварія на водопроводі','2025-09-24','16:45:00'),(4,1,'0934445566','Ігор','Загоряння проводки','Сильне задимлення у приватному будинку.','вул. Квітня, 98','Коротке замикання','2025-09-25','09:10:00'),(5,5,'0667778899','Власник','Пожежа на складі','Сильна пожежа, є загроза поширення.','пр. Перемоги, 50','Порушення ППБ','2025-09-26','11:00:00'),(6,2,'0960001122','Петро','Зіткнення на трасі','Фура та легковий автомобіль зіткнулися.','Траса М-06, 11','Недотримання дистанції','2025-09-26','14:30:00'),(7,4,'0503334455','ЖЕК','Прорив труби','Прорив магістральної труби на вулиці.','вул. Городоцька, 5','Зношеність мереж','2025-09-27','08:00:00'),(8,1,'0676667788','Марія','Дим у під\'їзді','Загоряння сміттєпроводу.','вул. Сахарова, 22','Недбалість','2025-09-28','19:00:00'),(9,3,'0990001122','ОСББ','Затоплення гаражів','Сильний дощ, не справляється каналізація.','вул. Стрийська, 100','Засмічення','2025-09-29','21:00:00'),(10,5,'0634445566','Охорона','Задимлення цеху','Задимлення в виробничому цеху.','вул. Промислова, 3','Поломка обладнання','2025-10-01','07:00:00'),(11,2,'0971230000','Свідок','ДТП 5 машин','Масова аварія на слизькій дорозі.','Кільцева дорога, 15','Ожеледиця','2025-10-01','10:30:00'),(12,1,'0679870000','Сусід','Запах газу','Підозра на витік газу в квартирі.','вул. Квітня, 5','Витік газу','2025-10-02','12:00:00'),(13,1,'0951112233','Ольга','Пожежа на балконі','Загоряння на балконі житлового будинку','пр. Свободи, 45','Недопалок','2025-10-05','18:00:00'),(14,4,'0675554433','Комунальник','Прорив теплотраси','На вулиці витікає гаряча вода','пл. Ринок, 1','Аварія','2025-10-10','06:00:00'),(15,2,'0998887766','Водій','ДТП, перевернута машина','Машина перекинулась, потрібна допомога.','Траса Н-10, 50','Втрата керування','2025-10-15','22:00:00');
/*!40000 ALTER TABLE `calls` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cities`
--

DROP TABLE IF EXISTS `cities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cities` (
  `city_id` int NOT NULL AUTO_INCREMENT,
  `city_name` varchar(45) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`city_id`),
  KEY `city_name_idx` (`city_name`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cities`
--

LOCK TABLES `cities` WRITE;
/*!40000 ALTER TABLE `cities` DISABLE KEYS */;
INSERT INTO `cities` VALUES (10,'Дніпро'),(7,'Житомир'),(1,'Київ'),(2,'Львів'),(3,'Одеса'),(6,'Суми'),(5,'Тернопіль'),(4,'Харків'),(8,'Чернівці'),(9,'Чернігів');
/*!40000 ALTER TABLE `cities` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `dist_backup_20251208220804_1`
--

DROP TABLE IF EXISTS `dist_backup_20251208220804_1`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dist_backup_20251208220804_1` (
  `name` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `city_id` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dist_backup_20251208220804_1`
--

LOCK TABLES `dist_backup_20251208220804_1` WRITE;
/*!40000 ALTER TABLE `dist_backup_20251208220804_1` DISABLE KEYS */;
INSERT INTO `dist_backup_20251208220804_1` VALUES ('Васильківський',4),('Київський',3),('Оболонський',1),('Подільський',1),('Сихівський',2),('Суворовський',3),('Яворівський',1);
/*!40000 ALTER TABLE `dist_backup_20251208220804_1` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `dist_backup_20251208220804_2`
--

DROP TABLE IF EXISTS `dist_backup_20251208220804_2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dist_backup_20251208220804_2` (
  `name` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `city_id` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dist_backup_20251208220804_2`
--

LOCK TABLES `dist_backup_20251208220804_2` WRITE;
/*!40000 ALTER TABLE `dist_backup_20251208220804_2` DISABLE KEYS */;
INSERT INTO `dist_backup_20251208220804_2` VALUES ('Личаківський',2),('Приморський',3),('Шевченківський',1);
/*!40000 ALTER TABLE `dist_backup_20251208220804_2` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `dist_backup_20251209175304_1`
--

DROP TABLE IF EXISTS `dist_backup_20251209175304_1`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dist_backup_20251209175304_1` (
  `name` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `city_id` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dist_backup_20251209175304_1`
--

LOCK TABLES `dist_backup_20251209175304_1` WRITE;
/*!40000 ALTER TABLE `dist_backup_20251209175304_1` DISABLE KEYS */;
INSERT INTO `dist_backup_20251209175304_1` VALUES ('Личаківський',2),('Оболонський',1),('Подільський',1),('Приморський',3),('Сихівський',2);
/*!40000 ALTER TABLE `dist_backup_20251209175304_1` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `dist_backup_20251209175304_2`
--

DROP TABLE IF EXISTS `dist_backup_20251209175304_2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dist_backup_20251209175304_2` (
  `name` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `city_id` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dist_backup_20251209175304_2`
--

LOCK TABLES `dist_backup_20251209175304_2` WRITE;
/*!40000 ALTER TABLE `dist_backup_20251209175304_2` DISABLE KEYS */;
INSERT INTO `dist_backup_20251209175304_2` VALUES ('Васильківський',4),('Київський',3),('Суворовський',3),('Шевченківський',1),('Яворівський',1);
/*!40000 ALTER TABLE `dist_backup_20251209175304_2` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `districts`
--

DROP TABLE IF EXISTS `districts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `districts` (
  `district_id` int NOT NULL AUTO_INCREMENT,
  `district_name` varchar(45) COLLATE utf8mb4_unicode_ci NOT NULL,
  `city_id` int NOT NULL,
  PRIMARY KEY (`district_id`,`city_id`),
  KEY `fk_district_city_idx` (`city_id`),
  CONSTRAINT `fk_district_city` FOREIGN KEY (`city_id`) REFERENCES `cities` (`city_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `districts`
--

LOCK TABLES `districts` WRITE;
/*!40000 ALTER TABLE `districts` DISABLE KEYS */;
INSERT INTO `districts` VALUES (1,'Шевченківський',1),(2,'Подільський',1),(3,'Сихівський',2),(4,'Франківський',2),(5,'Приморський',3),(6,'Київський',3),(7,'Оболонський',1),(8,'Личаківський',2),(9,'Суворовський',3),(10,'Дарницький',1);
/*!40000 ALTER TABLE `districts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `dummy_table`
--

DROP TABLE IF EXISTS `dummy_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dummy_table` (
  `id` int NOT NULL AUTO_INCREMENT,
  `val` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dummy_table`
--

LOCK TABLES `dummy_table` WRITE;
/*!40000 ALTER TABLE `dummy_table` DISABLE KEYS */;
INSERT INTO `dummy_table` VALUES (1,'Noname1'),(2,'Noname2'),(3,'Noname3'),(4,'Noname4'),(5,'Noname5'),(6,'Noname6'),(7,'Noname7'),(8,'Noname8'),(9,'Noname9'),(10,'Noname10'),(11,'Noname1'),(12,'Noname2'),(13,'Noname3'),(14,'Noname4'),(15,'Noname5'),(16,'Noname6'),(17,'Noname7'),(18,'Noname8'),(19,'Noname9'),(20,'Noname10');
/*!40000 ALTER TABLE `dummy_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `emergencytypes`
--

DROP TABLE IF EXISTS `emergencytypes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `emergencytypes` (
  `emergency_type_id` int NOT NULL AUTO_INCREMENT,
  `type_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`emergency_type_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `emergencytypes`
--

LOCK TABLES `emergencytypes` WRITE;
/*!40000 ALTER TABLE `emergencytypes` DISABLE KEYS */;
INSERT INTO `emergencytypes` VALUES (1,'Пожежа в житловому будинку'),(2,'ДТП на трасі'),(3,'Затоплення підвалу'),(4,'Аварія на водопроводі'),(5,'Пожежа на промисловому об\'єкті'),(6,'Пожежа на відкритій місцевості'),(7,'ДТП у місті'),(8,'Затоплення будинку'),(9,'Аварія на промисловості'),(10,'Втоплення на водоймі');
/*!40000 ALTER TABLE `emergencytypes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `equipment_log`
--

DROP TABLE IF EXISTS `equipment_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `equipment_log` (
  `log_id` int NOT NULL AUTO_INCREMENT,
  `msg` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `log_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`log_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `equipment_log`
--

LOCK TABLES `equipment_log` WRITE;
/*!40000 ALTER TABLE `equipment_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `equipment_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fire_equipments`
--

DROP TABLE IF EXISTS `fire_equipments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fire_equipments` (
  `equipment_id` int NOT NULL AUTO_INCREMENT,
  `equipment_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `department_id_fk` int NOT NULL,
  PRIMARY KEY (`equipment_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fire_equipments`
--

LOCK TABLES `fire_equipments` WRITE;
/*!40000 ALTER TABLE `fire_equipments` DISABLE KEYS */;
INSERT INTO `fire_equipments` VALUES (1,'Шолом',77);
/*!40000 ALTER TABLE `fire_equipments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `firedepartments`
--

DROP TABLE IF EXISTS `firedepartments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `firedepartments` (
  `fire_department_id` int NOT NULL AUTO_INCREMENT,
  `fire_department_name` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  `district_id` int NOT NULL,
  `adress` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`fire_department_id`),
  KEY `fk_district_firedepartments_idx` (`district_id`),
  CONSTRAINT `fk_district_firedepartments` FOREIGN KEY (`district_id`) REFERENCES `districts` (`district_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=78 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `firedepartments`
--

LOCK TABLES `firedepartments` WRITE;
/*!40000 ALTER TABLE `firedepartments` DISABLE KEYS */;
INSERT INTO `firedepartments` VALUES (1,'ДПРЧ-1 (Центр Київ)',1,'вул. Володимирська, 15'),(2,'ДПРЧ-2 (Поділ)',2,'вул. Подільська, 5'),(3,'ДПРЧ-3 (Сихів Львів)',3,'пр. Червоної Калини, 55'),(4,'ДПРЧ-4 (Франка)',4,'вул. В. Великого, 1'),(5,'ДПРЧ-5 (Приморський Одеса)',5,'пр. Шевченка, 20'),(6,'ДПРЧ-6 (Київський Одеса)',6,'вул. Корольова, 15'),(7,'ДПРЧ-7 (Оболонь)',7,'пр. Героїв Майдану, 5'),(8,'ДПРЧ-8 (Дарниця)',10,'пр. Бажана, 15'),(9,'ДПРЧ-9 (Личаків)',8,'вул. Пасічна, 12'),(10,'ДПРЧ-10 (Резерв)',1,'вул. Резервна, 1'),(66,'Частина 90',6,'Резервна адреса'),(77,'Частина 10',3,'вул. Сяйво, 11');
/*!40000 ALTER TABLE `firedepartments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `package_table`
--

DROP TABLE IF EXISTS `package_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `package_table` (
  `id` int NOT NULL AUTO_INCREMENT,
  `val` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `package_table`
--

LOCK TABLES `package_table` WRITE;
/*!40000 ALTER TABLE `package_table` DISABLE KEYS */;
INSERT INTO `package_table` VALUES (1,'Noname1'),(2,'Noname2'),(3,'Noname3'),(4,'Noname4'),(5,'Noname5'),(6,'Noname6'),(7,'Noname7'),(8,'Noname8'),(9,'Noname9'),(10,'Noname10'),(11,'Noname1'),(12,'Noname2'),(13,'Noname3'),(14,'Noname4'),(15,'Noname5'),(16,'Noname6'),(17,'Noname7'),(18,'Noname8'),(19,'Noname9'),(20,'Noname10'),(21,'Noname1'),(22,'Noname2'),(23,'Noname3'),(24,'Noname4'),(25,'Noname5'),(26,'Noname6'),(27,'Noname7'),(28,'Noname8'),(29,'Noname9'),(30,'Noname10');
/*!40000 ALTER TABLE `package_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rescuers`
--

DROP TABLE IF EXISTS `rescuers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rescuers` (
  `rescuers_id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(45) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_name` varchar(45) COLLATE utf8mb4_unicode_ci NOT NULL,
  `rang` varchar(45) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`rescuers_id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rescuers`
--

LOCK TABLES `rescuers` WRITE;
/*!40000 ALTER TABLE `rescuers` DISABLE KEYS */;
INSERT INTO `rescuers` VALUES (1,'Іван','Петренко','Капітан'),(2,'Олександр','Коваль','Сержант'),(3,'Віктор','Сидоренко','Лейтенант'),(4,'Ірина','Ткачук','Рядовий'),(5,'Сергій','Лисенко','Майор'),(6,'Микола','Мельник','Капітан'),(7,'Андрій','Шевченко','Сержант'),(8,'Юлія','Іванова','Лейтенант'),(9,'Володимир','Кравчук','Майор'),(10,'Олена','Мороз','Рядовий'),(11,'Дмитро','Савчук','Капітан'),(12,'Артем','Бабій','Сержант'),(13,'Роман','Григоренко','Рядовий'),(14,'Павло','Захарчук','Рядовий'),(15,'Олег','Бондаренко','Лейтенант');
/*!40000 ALTER TABLE `rescuers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rescuersinjury`
--

DROP TABLE IF EXISTS `rescuersinjury`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rescuersinjury` (
  `injury_id` int NOT NULL AUTO_INCREMENT,
  `call_participation_id` int NOT NULL,
  `injury_description` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `hospital_name` varchar(250) COLLATE utf8mb4_unicode_ci NOT NULL,
  `diagnosis` varchar(250) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`injury_id`),
  KEY `fk_injury_callparticipation` (`call_participation_id`),
  CONSTRAINT `fk_injury_callparticipation` FOREIGN KEY (`call_participation_id`) REFERENCES `callparticipation` (`call_participation_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rescuersinjury`
--

LOCK TABLES `rescuersinjury` WRITE;
/*!40000 ALTER TABLE `rescuersinjury` DISABLE KEYS */;
INSERT INTO `rescuersinjury` VALUES (1,3,'Вивих плеча','Міська лікарня №1','Вивих'),(2,7,'Опік 1-го ступеня','Опіковий центр','Термічний опік'),(3,16,'Струс мозку','Травмпункт','Струс'),(4,1,'Отруєння чадним газом','Лікарня №3','Отруєння'),(5,20,'Перелом ноги','Обласна лікарня №1','Складний перелом'),(6,10,'Вивих плеча','Міська лікарня №1','Вивих'),(7,8,'Опік 2-го ступеня','Опіковий центр','Термічний опік'),(8,14,'Струс мозку','Травмпункт','Струс'),(9,6,'Отруєння чадним газом','Лікарня №1','Отруєння'),(10,18,'Перелом руки','Обласна лікарня №2','Складний перелом');
/*!40000 ALTER TABLE `rescuersinjury` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vehicles`
--

DROP TABLE IF EXISTS `vehicles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `vehicles` (
  `vehicle_id` int NOT NULL AUTO_INCREMENT,
  `fire_department_id` int NOT NULL,
  `type_id` int NOT NULL,
  `brand` varchar(45) COLLATE utf8mb4_unicode_ci NOT NULL,
  `model` varchar(45) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`vehicle_id`),
  KEY `fk_vehicle_firedepartment` (`fire_department_id`),
  KEY `fk_vehicle_type` (`type_id`),
  CONSTRAINT `fk_vehicle_firedepartment` FOREIGN KEY (`fire_department_id`) REFERENCES `firedepartments` (`fire_department_id`),
  CONSTRAINT `fk_vehicle_type` FOREIGN KEY (`type_id`) REFERENCES `vehicletypes` (`vehicle_types_id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vehicles`
--

LOCK TABLES `vehicles` WRITE;
/*!40000 ALTER TABLE `vehicles` DISABLE KEYS */;
INSERT INTO `vehicles` VALUES (1,1,1,'МАЗ','5337'),(2,1,3,'МАЗ','5550'),(3,2,1,'MAN','TGL'),(4,2,4,'МАЗ','4371'),(5,3,1,'ЗІЛ','130'),(6,3,2,'ГАЗ','3302'),(7,4,1,'KRAZ','6511'),(8,4,3,'KRAZ','6322'),(9,5,1,'КАМАЗ','65115'),(10,5,4,'КАМАЗ','43118'),(11,6,1,'МАЗ','5337'),(12,7,2,'MERCEDES','SPRINTER'),(13,8,1,'МАЗ','5550'),(14,9,3,'MAN','TGL'),(15,10,1,'ЗІЛ','130');
/*!40000 ALTER TABLE `vehicles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vehicletypes`
--

DROP TABLE IF EXISTS `vehicletypes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `vehicletypes` (
  `vehicle_types_id` int NOT NULL AUTO_INCREMENT,
  `type_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`vehicle_types_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vehicletypes`
--

LOCK TABLES `vehicletypes` WRITE;
/*!40000 ALTER TABLE `vehicletypes` DISABLE KEYS */;
INSERT INTO `vehicletypes` VALUES (1,'Основна пожежна машина'),(2,'Рятувально-аварійна'),(3,'Автоцистерна'),(4,'Автодрабина'),(5,'Додаткова пожежна машина'),(6,'Рятувальна машина'),(7,'Автокран'),(8,'Автодрабина велика'),(9,'Піротехнічна машина'),(10,'Броньована для евакуації');
/*!40000 ALTER TABLE `vehicletypes` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-06 23:23:20
