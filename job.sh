#!/bin/sh
# chmod u+x job.sh to give permission to script
for j in {5..9} # Months
do
  for i in {1..8} # Days
  do
    k=$((i+1))
    python3 check_wordpress.py --r_host localhost --r_username root --r_password root --r_db_name wordpress_db --r_table_id 0 --day_from '2019-0'"$j"'-0'"$i"'-''00:00:00' --day_to '2019-0'"$j"'-0'"$k"'-''00:00:00' --w_host localhost --w_username root --w_password root --w_db_name wordpress_db --cores 4
  done
  python3 check_wordpress.py --r_host localhost --r_username root --r_password root --r_db_name wordpress_db --r_table_id 0 --day_from '2019-0'"$j"'-09-00:00:00' --day_to '2019-0'"$j"'-10-00:00:00' --w_host localhost --w_username root --w_password root --w_db_name wordpress_db --cores 4
  for i in {10..30}
  do
    k=$((i+1))
    python3 check_wordpress.py --r_host localhost --r_username root --r_password root --r_db_name wordpress_db --r_table_id 0 --day_from '2019-0'"$j"'-'"$k"'-''00:00:00' --day_to '2019-0'"$j"'-'"$k"'-''00:00:00' --w_host localhost --w_username root --w_password root --w_db_name wordpress_db --cores 4
  done
done
#
# for j in {10..11} # Months
# do
#   for i in {1..8} # Days
#   do
#     k=$((i+1))
#     python3 check_wordpress.py --r_host localhost --r_username root --r_password root --r_db_name wordpress_db --r_table_id 0 --day_from '2019-'"$j"'-0'"$i"'-''00:00:00' --day_to '2019-'"$j"'-0'"$k"'-''00:00:00' --w_host localhost --w_username root --w_password root --w_db_name wordpress_db --cores 4
#   done
#   python3 check_wordpress.py --r_host localhost --r_username root --r_password root --r_db_name wordpress_db --r_table_id 0 --day_from '2019-'"$j"'-09-00:00:00' --day_to '2019-'"$j"'-10-00:00:00' --w_host localhost --w_username root --w_password root --w_db_name wordpress_db --cores 4
#   for i in {10..30}
#   do
#     k=$((i+1))
#     python3 check_wordpress.py --r_host localhost --r_username root --r_password root --r_db_name wordpress_db --r_table_id 0 --day_from '2019-'"$j"'-'"$k"'-''00:00:00' --day_to '2019-'"$j"'-'"$k"'-''00:00:00' --w_host localhost --w_username root --w_password root --w_db_name wordpress_db --cores 4
#   done
# done
