from django.db import models

# Define the data model for our tables
#
# Notes
# =====
#
# - How do we select Postgres?
# - What are all of the possible field types? (CharField, Int, Text, etc?)
# - How do we define primary keys?
# - How do we define indexes?
#
# ============================================================================

# HECTOR:
# CREATE TABLE IF NOT EXISTS `host` (
#   `host_id` INT NOT NULL AUTO_INCREMENT,
#   `host_ip` VARCHAR(15) NOT NULL,
#   `host_ip_numeric` INT UNSIGNED NOT NULL,
#   `host_name` TINYTEXT NOT NULL,
#   `host_os` VARCHAR(100) DEFAULT NULL,
#   `host_os_family` VARCHAR(100) DEFAULT NULL,
#   `host_os_type` VARCHAR(100) DEFAULT NULL,
#   `host_os_vendor` VARCHAR(100) DEFAULT NULL,
#   `host_link` VARCHAR(255) DEFAULT NULL,
#   `host_note` TEXT DEFAULT NULL,
#   `host_sponsor` VARCHAR(50) DEFAULT NULL, -- faculty/staff contact
#   `host_technical` VARCHAR(255) DEFAULT NULL, -- technical contact
#   `supportgroup_id` INT DEFAULT NULL, -- responsible lsp
#   `host_verified` tinyint(1) DEFAULT '0', -- has the information been vetted
#   `host_ignored` tinyint(1) DEFAULT '0', -- Don't check this host?
#   `host_policy` tinyint(1) DEFAULT '0', -- Policy (i.e. "falls under confidential data policy")
#   `location_id` INT DEFAULT NULL,
#   `host_ignore_portscan` TINYINT(1) DEFAULT 0,
#   `host_ignoredby_user_id` INT DEFAULT NULL,
#   `host_ignoredfor_days` INT DEFAULT 0,
#   `host_ignored_timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#   `host_ignored_note` TEXT DEFAULT NULL,
#   PRIMARY KEY  (`host_id`),
#   INDEX (`location_id`),
#   INDEX (`host_ip`),
#   INDEX (`host_ip_numeric`),
#   INDEX (`supportgroup_id`)
# ) ENGINE = INNODB;

class Hosts(models.model):
    ipv4_address = models.IPAddressField()
    hostname = models.CharField(max_length=50)
    lsp = models.IntegerField
    os = models.CharField(max_length=75)
    os_family = models.CharField(max_length=75)
    os_type = models.CharField(max_length=75)
    os_vendor = models.CharField(max_length=75)
    link = models.CharField(max_length=255)
    note = models.TextField()


