# import mysql.connector
# mydb = mysql.connector.connect(
#       host = "127.0.0.1",
#       user = "root",
#       passwd = "root"
#   )
# mycursor = mydb.cursor()
# mycursor.execute("USE wordpress_db")
# sql =  "CREATE TABLE summary_0 (formID BIGINT(20) NOT NULL,key VARCHAR(100) NOT NULL, item VARCHAR(500) NOT NULL, value INT(10) UNSIGNED NOT NULL,from TIMESTAMP NOT NULL, to TIMESTAMP NOT NULL)"
# mycursor.execute(sql)
#
# # CREATE TABLE `wordpress_db`.`summary_0` ( `formID` BIGINT(20) NOT NULL , `key` VARCHAR(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL , `item` VARCHAR(500) NOT NULL , `value` INT(10) UNSIGNED NOT NULL , `from` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP , `to` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ) ENGINE = InnoDB CHARSET=utf8 COLLATE utf8_unicode_ci;
import os.path
print(os.path.isfile('errors.txt'))
