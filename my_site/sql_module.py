import pyodbc
import pandas


class WordSQL():
	def __init__(self,word, translation, transcription, example):
		self.word = word
		self.translation = translation
		self.transcription = transcription
		self.example = example
	def __str__(self):
		return self.word
	def __repr__(self):
		return self.word + " " + self.translation + " " + self.transcription
	def write_word_to_sql(self,cursor):
		try:
			cursor.execute(self.get_expression())
			cursor.commit()
		except:
			print("can't write data to SQL server!")
	def get_expression(self):
		expr_columns = "(id,word,translation,transcription,first_letter, example)"
		expr = "INSERT INTO Words" + expr_columns + "VALUES (NEWID(), '{}','{}','{}','{}','{}')"
		expr = expr.format(self.word,self.translation,self.transcription,self.word[0],self.example)
		return expr

word = {'word': 'lake'}

def delete_data_from_table(table_name, cursor):
	expr = "DELETE FROM " + table_name
	print(expr)
	cursor.execute(expr)
	cursor.commit()


def get_connection_to_sql_server():
	server = r'DESKTOP-H6C2946\SQLEXPRESS' 
	database = 'Study' 
	username = 'ingray' 
	password = 'sqlserver' 
	connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
	return connection

def get_cursor():
	connection = get_connection_to_sql_server()
	cursor = connection.cursor()
	return cursor

def get_all_table(connection, table_name):
	cursor = connection.cursor()
	my_table = cursor.execute("SELECT * FROM Words")
	return my_table


# my_words = get_all_table(get_connection_to_sql_server(), "Words")
# for x in my_words:
# 	print(x)


def add_row(cursor,dict_object,table_name,id_needed = False):
	columns_str = "("
	values_str = ""
	print(dict_object)
	print(type(dict_object))
	if id_needed:
		columns_str = "(id , "
		values_str = "NEWID()," 
	for x in dict_object.keys():
		columns_str = columns_str + x
		values_str = values_str + "'" +dict_object[x]+"'";
	columns_str = columns_str + ") "
	print(columns_str)
	print(values_str)
	expr = "INSERT INTO " + table_name + columns_str + "VALUES("+ values_str +")"
	print(expr)
	cursor.execute(expr)
	cursor.commit()
	print("!")

# add_row(get_cursor(),word,"Words",True)

new_word = WordSQL("tree","дерево","три","Trees are very important part of any park")
print(new_word.get_expression())
new_word.write_word_to_sql(get_cursor())
delete_data_from_table("Words", get_cursor())