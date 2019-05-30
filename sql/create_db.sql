CREATE DATABASE IF NOT EXISTS `events_anomaly` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */;

USE `events_anomaly`;

CREATE TABLE IF NOT EXISTS `Event` 
(
  `event_id`                    int(11) unsigned                      NOT NULL AUTO_INCREMENT,
  `occurrence_timestamp`        timestamp(3)                          NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`event_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `EventCount` 
(
  `event_count_id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `dt_bucket` 		DATETIME(6) NOT NULL,
  `actual_count` 		INT(11) UNSIGNED NOT NULL,
  PRIMARY KEY (`event_count_id`),
  UNIQUE INDEX `ix_dt_bucket_u` (`dt_bucket` ASC)
) ENGINE = InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `ModelType` 
(
  `model_type_id` 	INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `model_type` 		VARCHAR(50) NOT NULL,
  PRIMARY KEY (`model_type_id`),
  UNIQUE INDEX `ix_model_type_u` (`model_type` ASC)
) ENGINE = InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `MetricType` 
(
  `metric_type_id` 	INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `metric_type` 		VARCHAR(50) NOT NULL,
  PRIMARY KEY (`metric_type_id`),
  UNIQUE INDEX `ix_metric_type_id_u` (`metric_type_id` ASC)
) ENGINE = InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `EventPredict`
(
  `event_predict_id` 	INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `event_count_id` 	INT(11) UNSIGNED NOT NULL,
  `model_type_id` 			INT(11) UNSIGNED NOT NULL,
  `metric_type_id` 			INT(11) UNSIGNED NOT NULL,
  `metric_dt` 		DATETIME(6) NOT NULL,
  `metric_value` 			DECIMAL(12,4) NOT NULL,
  PRIMARY KEY (`event_predict_id`),
  INDEX `ix_event_count_id_nu` (`event_count_id` ASC),
  INDEX `ix_model_type_id_nu` (`model_type_id` ASC),
  INDEX `ix_metric_type_id_nu` (`metric_type_id` ASC),
  CONSTRAINT `fk_event_count_id`
    FOREIGN KEY (`event_count_id`)
      REFERENCES `EventCount` (`event_count_id`)
      ON DELETE NO ACTION
      ON UPDATE NO ACTION,
  CONSTRAINT `fk_model_type_id`
    FOREIGN KEY (`model_type_id`)
      REFERENCES `ModelType` (`model_type_id`)
      ON DELETE NO ACTION
      ON UPDATE NO ACTION,
  CONSTRAINT `fk_metric_type_id`
    FOREIGN KEY (`metric_type_id`)
      REFERENCES `MetricType` (`metric_type_id`)
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
) ENGINE = InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `ModelType` (`model_type_id`, `model_type`) VALUES (1, 'LINEAR');

INSERT INTO `MetricType` (`metric_type_id`, `metric_type`) VALUES (1, 'ANOMALY');
INSERT INTO `MetricType` (`metric_type_id`, `metric_type`) VALUES (2, 'PREDICTION');
INSERT INTO `MetricType` (`metric_type_id`, `metric_type`) VALUES (3, 'STDDEV');
INSERT INTO `MetricType` (`metric_type_id`, `metric_type`) VALUES (4, 'ACTUAL');
INSERT INTO `MetricType` (`metric_type_id`, `metric_type`) VALUES (5, 'UP_BOUND');
INSERT INTO `MetricType` (`metric_type_id`, `metric_type`) VALUES (6, 'LOW_BOUND');








