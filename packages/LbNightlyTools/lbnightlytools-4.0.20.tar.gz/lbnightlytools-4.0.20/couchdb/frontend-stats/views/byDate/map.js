function(doc) {
    if (doc.type == "slot-info") {
        if(doc.date != null){
           to_emit = {};
           to_emit['slot'] = doc['slot'];
           to_emit['build_id'] = doc['build_id'];
           to_emit['platforms'] = {}
           for(c_platform in doc['config']['platforms']){
                platform = doc['config']['platforms'][c_platform]
                to_emit['platforms'][platform] = {}
                for(c in doc['config']['projects']){
                    build_errors = 0
                    build_warnings = 0
                    test_errors = 0
                    test_passed = 0
                    test_failed = 0
                    test_untested = 0
                    if(doc['config']['projects'][c]['disabled'])
                        continue
                    project = doc['config']['projects'][c]['name']
                    build = doc['builds']
                    if (build && build[platform] && build[platform][project]){
                        build_errors = build[platform][project]['errors'];
                        build_warnings = build[platform][project]['warnings'];
                    }
                    tests = doc['tests']
                    if (tests && tests[platform] && tests[platform][project]){
                        tmp = tests[platform][project]['results'];
                        if(tmp){
                            if(tmp['FAIL']){
                                test_failed = tmp['FAIL'].length
                            }
                            if(tmp['PASS']){
                                test_passed = tmp['PASS'].length
                            }
                            if(tmp['UNTESTED']){
                                test_untested = tmp['UNTESTED'].length
                            }
                            if(tmp['ERROR']){
                                test_errors = tmp['ERROR'].length
                            }
                        }
                    }

                    to_emit['platforms'][platform][project] = {
                        'build_errors': build_errors,
                        'build_warnings': build_warnings,
                        'test_errors': test_errors,
                        'test_passed': test_passed,
                        'test_failed': test_failed,
                        'test_untested': test_untested
                    }
                }
           }
           emit(doc.date, to_emit);
        }
    }
}
