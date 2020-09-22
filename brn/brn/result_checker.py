def shouldbe(results: Kbs, shouldbe_kb: Kb) -> bool
    if (sb.first.empty() && sb.second.empty()) {
        return results.empty();
    }
    dout << "results.size()" << results.size() << endl;
    if(!results.size())
        return false;
    auto r = results.front();
    results.pop_front();
    return qdbs_equal(r, sb);

