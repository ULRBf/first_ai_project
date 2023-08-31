import os

if __name__ == '__main__':
    os.system('pyuic5 ./ui_main_form.ui -o ui_main_form.py')
    os.system('pyuic5 ./ui_join_form.ui -o ui_join_form.py')
    os.system('pyuic5 ./search_ui.ui -o search_ui.py')
    print("Complete")