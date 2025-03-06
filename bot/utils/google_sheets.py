import gspread

gc = gspread.service_account("creds.json")
admin_sheet = gc.open("TaskBotAdmins").sheet1

admins_id = set(admin_sheet.col_values(1)[1:])
responsible_id = set(admin_sheet.col_values(2)[1:])
chat_id = set(admin_sheet.col_values(3)[1:])

def set_image_id(image_id):
    column_values = admin_sheet.col_values(4) 

    next_row = len(column_values) + 1
    
    admin_sheet.update_cell(next_row, 4, image_id)