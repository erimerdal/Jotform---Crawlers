import argparse
import langdetect
from langdetect import detect_langs as detect_langs
import pymysql
import sys

def which_language(lang):
    result_lang = detect_langs(lang)
    # A dictionary shows which [ISO 639-1 codes] corresponds to which lang
    languages = {"af":"Afrikaans","ar":"Arabic","bg":"Bulgarian","bn":"Bengali","ca":"Catalan/Valencian","cs":"Czech"
    ,"cy":"Welsh","da":"Danish","de":"German","el":"Greek,Modern","en":"English","es":"Spanish","et":"Estonian","fa":"Persian","fi":"Finnish",
    "fr":"French","gu":"Gujarati","he":"Hebrew", "hi":"Hindi", "hr":"Croatian", "hu":"Hungarian", "id":"Indonesian", "it":"Italian", "ja":"Japanese",
     "kn":"Kannada", "ko":"Korean","lt":"Lithuanian", "lv":"Latvian", "mk":"Macedonian", "ml":"Malayalam", "mr":"Marathi", "ne":"Nepali", "nl":"Dutch/Flemish",
      "no":"Norwegian", "pa":"Punjabi", "pl":"Polish", "pt":"Portugese", "ro":"Romanian", "ru":"Russian", "sk":"Slovak", "sl":"Slovenian",
       "so":"Somali", "sq":"Albanian", "sv":"Swedish", "sw":"Swahili", "ta":"Tamil", "te":"Telugu", "th":"Thai", "tl":"Tagalog", "tr":"Turkish",
        "uk":"Ukranian", "ur":"Urdu", "vi":"Vietnamese", "zh-cn":"Chinese", "zh-tw":"Chinese"}

    language_confidence = str(result_lang[0]).split(':')
    return [languages[language_confidence[0]],language_confidence[1]]

def controller(args):
    try:
        read_db = pymysql.connect(
            host = args.r_host,
            user = args.r_username,
            passwd = args.r_password,
            database = args.r_db_name
        )

        write_db = pymysql.connect(
            host = args.w_host,
            user = args.w_username,
            passwd = args.w_password,
            database = args.w_db_name
        )

    except pymysql.Error as db_error:
        print("Database connection error while reading: ", db_error)
    else:
        f = open('lang_insert_2.sql', 'a+')
        # Create table if not exists
        write_cursor = write_db.cursor()
        write_cursor.execute("CREATE TABLE IF NOT EXISTS language_data_2 (id VARCHAR(255) PRIMARY KEY, language VARCHAR(255), confidence VARCHAR(255))")

        # Insert sql here to get the data
        read_cursor = read_db.cursor()
        # Using the data
        read_cursor.execute("SELECT answer.id, answer.question, answer.details FROM answer")
        data = read_cursor.fetchall()
        count = 0

        insert_sql = []
        insert_sql.append("INSERT IGNORE INTO language_data_2 (id, language, confidence) VALUES ")
        insert = False

        for row in data:
            print("Row #: %s / %s ", (count,len(data)))
            count += 1
            question_language = ["",""]
            details_language = ["",""]
            language = ""
            try:
                question_language = which_language(row[1])

            except langdetect.lang_detect_exception.LangDetectException:
                pass
            try:
                details_language = which_language(row[2])
            except langdetect.lang_detect_exception.LangDetectException:
                pass
            if question_language[0] == details_language[0]:
                language = question_language[0]
                confidence = question_language[1]
            else:
                if question_language[1] >= details_language[1]:
                    language = question_language[0]
                    confidence = question_language[1]
                else:
                    language = details_language[0]
                    confidence = details_language[1]

            val = (str(row[0]), str(language), str(confidence))
            sql = "('%s', '%s', '%s'), " % val # Insert error code or non_wp
            insert_sql.append(sql)

        insert_sql_string = ''.join(insert_sql)
        # Execute the SQL created
        insert_sql_string = insert_sql_string[:len(insert_sql_string)-2]
        write_cursor.execute(insert_sql_string)
        f.write(insert_sql_string)
        f.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--r_host')
    parser.add_argument('--r_username')
    parser.add_argument('--r_password')
    parser.add_argument('--r_db_name')

    parser.add_argument('--w_host')
    parser.add_argument('--w_username')
    parser.add_argument('--w_password')
    parser.add_argument('--w_db_name')
    args = parser.parse_args()
    controller(args)


if __name__ == '__main__':
    main()
