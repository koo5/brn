def shouldbe(qdb &sb) {
    if (INPUT->do_query)
        test_result(_shouldbe(tauProver->results, sb));
    if (INPUT->do_cppout) {
        bool r = _shouldbe(cppout_results, sb);
        dout << "cppout:";
        test_result(r);
    }
    if (!INPUT->external.empty()) {
        bool r = _shouldbe(external_results, sb);
        dout << "external:";
        test_result(r);
    }
}



void thatsall()
{
    test_result(tauProver->results.empty());
}

void clear_kb(){
    kbs.clear();
}




"""
the test runner is aware of different RDF formats. This is because otherwise, among other things, we'd have to provide a way to specify, perhaps within testcases, how to inform the various possibly invoked reasoners of the file format(s). If a reasoner would guess this from file extension, the test runner would have to know what extension to use, when generating the files for the reasoner.      
