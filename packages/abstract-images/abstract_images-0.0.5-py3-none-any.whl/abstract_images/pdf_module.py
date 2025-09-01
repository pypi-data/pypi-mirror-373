"""
pdf_console.py - GUI-Based PDF Editor

This script provides a graphical interface for editing PDF files. It allows users to select,
separate, collate, and perform various operations on PDF files. The functions in this script
interact with utilities provided in the `image_utils.py` and `pdf_tools.py` modules.

Author: putkoff
GitHub Repository: https://github.com/AbstractEndeavors/abstract_essentials/tree/main/abstract_images
Contact Email: partners@abstractendeavors.com
Date: 08/27/2023
Version: 0.0.0.1
"""
import os
from abstract_gui import AbstractWindowManager,create_window_manager,get_window,get_gui_fun,expandable
from pdf_utils import get_directory,get_pdf_obj,get_ext,read_pdf,save_pdf,is_pdf_path,get_separate_pages,get_pdf_pages
from abstract_utilities.type_utils import ensure_integer
window_mgr = AbstractWindowManager()
def get_values(window=None, st:any=None):
    """
    Retrieves values from the GUI window manager.
    
    Args:
        window: A reference to the GUI window.
        st: A string key for the specific value to be fetched.
    
    Returns:
        The value associated with the provided key, if specified.
        Otherwise, returns the entire set of values from the window manager.
    """
    values = window_mgr.get_values()
    print(values)
    if st in values:
        return values[st]
def update_values(window:type(get_window())=None, key:str=None, value=None,values=None, args:dict={}):
    """
    Updates values in the GUI window manager.
    
    Args:
        window: A reference to the GUI window.
        key: The key associated with the value to be updated.
        value: The new value for the specified key.
        args: Additional arguments for the update operation.
    """
    if value != None:
        args["value"]=value
    if values != None:
        args["values"]=values
    window_mgr.update_values(window=window,key=key,args=args)
def get_page_selection_section():
    """
    Constructs the page selection section in the GUI.
    
    Returns:
        A GUI component for page selection.
    """
    page_start = get_gui_fun('Input',{"size":(5,1),"key":"-PAGE_START-","enable_events":True})
    page_end = get_gui_fun('Input',{"size":(5,1),"key":"-PAGE_END-","enable_events":True})
    return get_gui_fun('Frame',{"title":"Section Select","layout":[[page_start,get_gui_fun('T',{"value":"-"}),page_end]]})
def folder_select(window:type(get_window())=None, path:str="-PDF_INPUT_LOCATION-"):
    """
    Populates the list of available PDF files in the specified folder.
    
    Args:
        window: A reference to the GUI window.
        path: The path of the directory to search for PDF files.
    """
    if window != None:
        if path in window_mgr.get_values():
            path = get_values(window=window, st=path)
    if path == '':
        path = os.getcwd()
    ls_select = []
    list_files = os.listdir(path)
    for each in list_files:
        if get_ext(each) == '.pdf':
            ls_select.append(each)
    update_values(window=window,key="-PDF_SELECTION-",args={"values":ls_select})
def separate_button_action(window):
    """
    Action associated with the 'separate' button. Separates a range of pages from a selected PDF.
    
    Args:
        window: A reference to the GUI window.
    """
    pdf_file_path = get_values(window=window, st="-PDF_PATH-")
    output_location = get_values(window=window, st="-PDF_SEPARATE_LOCATION-")
    output_name = get_values(window=window, st="-SEPERATE_FOLDER_NAME-")
    start_page = int(get_values(window=window, st="-PAGE_START-"))
    end_page = int(get_values(window=window, st="-PAGE_END-"))
    if is_pdf_path(pdf_file_path):
        pdf_obj = read_pdf(pdf_file_path)
        pdf_writer = get_separate_pages(pdf_obj, start_page=start_page, end_page=end_page)
        output_file_path = os.path.join(output_location, output_name+'.pdf')
        save_pdf(output_file_path, pdf_writer)
        sg.popup('Success',text='PDF separation completed successfully!')
def while_events(event):
    """
    Event handler function for various GUI events. Handles button presses, list selection, and other interactive components.
    
    Args:
        event: The event that triggered the function call.
    """
    if event == "-LIST_BUTTON-":
        update_values(window=window,key="-PDF_SELECTION-",args={"values":folder_select(window, get_values(window=window, st="-PDF_INPUT_LOCATION-"))})
    if "PAGE_" in event:
        pages = get_pdf_pages(os.path.join(get_values(window=window,st="-PDF_INPUT_LOCATION-"),js_bridge["selected_pdf"]))
        page_value = window_mgr.get_values(window=window)[event]
        if event == "-PAGE_START-":
            page_value=int(ensure_integer(page_value, 0))
            window_mgr.update_values(window=window,key="-PAGE_START-",value=page_value)
            value_end = ensure_integer(window_mgr.get_values(window=window)["-PAGE_END-"],pages)
            if page_value > value_end:
                update_values(window=window,key="-PAGE_START-",args={"value":value_end})
            if pages < value_end:
                update_values(window=window,key="-PAGE_END-",args={"value":pages})
        else:
            page_value=int(ensure_integer(page_value, pages))
            window_mgr.update_values(window=window,key="-PAGE_END-",value=page_value)
            value_start = ensure_integer(window_mgr.get_values(window=window)["-PAGE_START-"],0)
            if pages < page_value:
                update_values(window=window,key="-PAGE_END-",args={"value":pages})
            if value_start > page_value:
                update_values(window=window,key="-PAGE_START-",args={"value":page_value})
        if page_value > pages:
            update_values(window=window,key=event,args={"value":pages})
        if page_value < 0:
            update_values(window=window,key=event,args={"value":0}) 
    if event == "-PDF_INPUT_LOCATION-":
        folder_select(window, values["-PDF_INPUT_LOCATION-"])
        update_values(window=window,key="-COLLATE_FOLDER-",args={"value":js_bridge["selected_pdf"]})
    if event == "-PDF_PATH-":
        update_values(window=window,key="-SEPERATE_PATH-",args={"value":get_values("-PDF_PATH-")})
    if event == "-PDF_SELECTION-":
        js_bridge["selected_pdf"] = get_values(window=window,st=event)[0]
        update_values(window=window,key="-PDF_PATH-",args={"value":os.path.join(get_values(window=window,st="-PDF_INPUT_LOCATION-"), js_bridge["selected_pdf"])})
        update_values(window=window,key="-SEPERATE_PATH-",args={"value":get_directory(os.path.join(get_values(window=window,st="-PDF_INPUT_LOCATION-"), js_bridge["selected_pdf"]))})
        update_values(window=window,key="-PAGE_START-",args={"value":0})
        update_values(window=window,key="-PAGE_END-",args={"value":get_pdf_pages(os.path.join(get_values(window=window,st="-PDF_INPUT_LOCATION-"),js_bridge["selected_pdf"]))})
    if event == "-SEPARATE_BUTTON-":
        separate_button_action(window)
    if event == "-COLLATE_FOLDER-":
        selected_collate_folder = get_values("-COLLATE_FOLDER-")
        pdf_files_in_folder = get_pdfs_in_directory(selected_collate_folder)
        update_values(window=window,key="-COLLATE_PDF_LIST-",args={"value":pdf_files_in_folder})
    if event == "-COLLATE_BUTTON-":
        collate_button_action(window)
if __name__ == "__main__":
    # Main execution and GUI loop
    pdf_selector = [[
        get_gui_fun('Frame',{"title":"pdf_files","layout":[[
        get_gui_fun('Listbox',{"values":[],"enable_events":True,"key":"-PDF_SELECTION-","size":(30,10)})]]})]]
    choose_pdf_location = [[
        get_gui_fun("Input",{"key":"-PDF_PATH-","enable_events":True}),
        get_gui_fun("FolderBrowse",{"key":"-PDF_INPUT_LOCATION-","enable_events":True})]]
    test_button =get_gui_fun('Button',{"button_text":"Generate List","key":"-LIST_BUTTON-","enable_events":True})
    collate_button =get_gui_fun('Button', {"button_text": "Collate", "key": "-COLLATE_BUTTON-", "enable_events": True})
    collate = [[
        get_gui_fun('Frame',{"title":"collate","layout":[[
            get_gui_fun('Button',{"button_text":"separate","key":"-SEPARATE_BUTTON-","enable_events":True}),
            get_gui_fun("Input",{"key":"-SEPERATE_PATH-","enable_events":True}),
            get_gui_fun("FolderBrowse",{"key":"-PDF_SEPARATE_LOCATION-","enable_events":True}),
            ],[get_gui_fun("T",{"text":"separate folder name"}),get_gui_fun("Input",{"key":"-SEPERATE_FOLDER_NAME-","enable_events":True})]]})]]            
    layout = [[test_button,get_page_selection_section()],choose_pdf_location,[pdf_selector],collate]
    window = window_mgr.add_window("PDF Manipulator",args={"layout":layout,**expandable(),"event_function":"while_events"})
    window_mgr.while_window()
