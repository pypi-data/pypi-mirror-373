


# tested only witexpected_format_type StringVariable ContinuousVariable
def check_data(dataset, expected_column_name, expected_format_type):
    """
    usage :
    if not check_data_in.check_data(dataset, "col_name", "StringVariable"):
        print("error")
        return
    -----
    return True if dataset ahas a column with title == expected_column_name (string)
                and if formats == expected "StringVariable" , "ContinuousVariable"
    else return False
    """
    if expected_column_name not in dataset.domain:
        return False
    variable_domain = dataset.domain[expected_column_name]
    if str(type(variable_domain))==expected_format_type:
        return True
    return False

def check_all_data(argself,dataset,list_expect_column_name,list_expect_format_type):
    """
    usage :
    if not check_data_in.check_all_data(self, dataset, ["col1_name", "col2_name"],
                                   ["StringVariable", "ContinuousVariable"]):
        return
   call check_data for all
   True if check is ok else False (in this case print error on widget)
    """
    if len(list_expect_column_name)!=len(list_expect_format_type):
        print("error dev not possible")
        return False
    list_error=""
    for idx in range(len(list_expect_column_name)):
        if check_data(dataset,list_expect_column_name[idx],list_expect_format_type[idx]):
            continue
        if list_error!="":
            list_error=list_error+"\n"
        list_error=list_error+"error with name/type column -> "+str(list_expect_column_name[idx])
    argself.error(list_error)
    if list_error=="":
        return True
    return False

