
def print_test_success(x:bool):
    dout << INPUT->name << ":test:";
    if (x)
        dout << KGRN << "PASS" << KNRM << endl;
    else
        dout << KRED << "FAIL" << KNRM << endl;
