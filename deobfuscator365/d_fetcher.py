'''
    Bet365 D_ Token Fetcher
    Author: @ElJaviLuki
'''

import subprocess
import re

PATH = './deobfuscator365/'

def fetch_D_token(bootjs_code: str):
    filename = PATH + 'd_fetcher.js'
    file = open(filename, "w")

    file.write(
        """try {
                const jsdom = require("jsdom");
                const { JSDOM } = jsdom;
        
                const { window: bootjs } = new JSDOM('', { 
                    url: "https://www.bet365.com",
                    runScripts: "outside-only" 
                });
                
                """
                    #   Fetch D_ token
                """
                
                function fetchHandshakeD_token(bootjsCode){
                    bootjs.eval(bootjsCode);
        
                    var fetchComposedToken = function(window) {
                        finalQ = '';
                        var tags = [
                            "Anchor",
                            "Audio",
                            "Body",
                            "Button",
                            "Canvas",
                            "Div",
                            "Form",
                            "Heading",
                            "IFrame",
                            "Image",
                            "Input",
                            "Label",
                            "Link",
                            "Media",
                            "Option",
                            "Paragraph",
                            "Pre",
                            "Select",
                            "Span",
                            "Style",
                            "TableCell",
                            "TableCol",
                            "Table",
                            "TableRow",
                            "TableSection",
                            "TextArea",
                            "Video"
                        ];
                        
                         for (var index = 0; index < tags.length; index++) {
                             var thisTag = tags[index]
                               , winElement = window["HTML" + thisTag + "Element"]
                               , theCaught = winElement.prototype.Caught;
                             if (!theCaught)
                                 continue;
                             var ownPropNames = Object.getOwnPropertyNames(Object.getPrototypeOf(theCaught));
                             for (var propIndex in ownPropNames) {
                                 var thisPropName = ownPropNames[propIndex]
                                   , protoFromThisCaught = Object.getPrototypeOf(theCaught[thisPropName])
                                   , subOPNs = Object.getOwnPropertyNames(protoFromThisCaught);
                                 for (var subOPNindex in subOPNs) {
                                     var thisSubOPN = subOPNs[subOPNindex];
                                     if (thisSubOPN in Object)
                                         continue;
                                     if (protoFromThisCaught[thisSubOPN] && protoFromThisCaught[thisSubOPN]()) {
                                         var composedToken = protoFromThisCaught[thisSubOPN]();
                                         finalQ = composedToken[0],
                                         initialN = composedToken[1];
                                         break;
                                     }
                                 }
                                 if (finalQ)
                                     break;
                             }
                             delete winElement.prototype.Caught;
                             if (finalQ)
                                 break;
                         }
                         return finalQ;
                    }
        
                    var transformNtoken = function(bootjs, URIComponent) {
                        decURI = decodeURIComponent(URIComponent);
                        var b64decodedSc = -bootjs.atob(initialN) % 0x40;
                        finalN = '';
                        for (var chIndex = 0; chIndex < decURI.length; chIndex++) {
                            var charCode = decURI.charCodeAt(chIndex);
                            var fromChar = String.fromCharCode((charCode+b64decodedSc) % 0x100);
                            finalN += fromChar;
                        }
                        return finalN;
                    }
        
                    var initialN = ''
                    var finalQ = fetchComposedToken(bootjs);
                    var HandJ = finalQ.split('.');
                    """
                        #   NOTE: N Token can be also fetched by Base-64 encoding the evaluated value in the expression
                        #         'ns_weblib_util.WebsiteConfig.SERVER_TIME+300'
                    """
                    var finalN = transformNtoken(bootjs, HandJ[0]);
                    var finalJ = HandJ[1];
                    var D_token = [finalN, '.', finalJ].join('');
                    return D_token;
                }
                
                """ 
                    #   String.raw`···`: avoids string escaping problems.
                """
                d_token = fetchHandshakeD_token(String.raw
                    `
                    """
                        #   Cancel some unneeded built-in functions that cause bugs during evaluation.
                        #   Note:   if you happen to find another bug that can be fixed by modifying a dependency, override
                        #           that dependency here:
                    """
                    overrideFunction = function() {}
                    XMLHttpRequest.prototype.open = overrideFunction;
                    XMLHttpRequest.prototype.send = overrideFunction;
                    
                    """ + str(bootjs_code) + """
                    `
                )
                
                console.log("<D_TOKEN>" + d_token + "</D_TOKEN>");
        } catch (error) {
            console.error(error);
        } finally {
            process.exit();
        }"""
    )

    file.close()

    result = subprocess.run(
        ['node', filename],
        text=True,
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if result.returncode == 0:
        delimitedToken = re.search("<D_TOKEN>(.*?)</D_TOKEN>", result.stdout).group()
        D_token = delimitedToken[len("<D_TOKEN>"):-len("</D_TOKEN>")]
    else:
        raise Exception('Error during token generation script evaluation or execution: ' + result.stderr)

    return D_token