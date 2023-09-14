/*
 * JavaScript client-side example using jsrsasign
 */

// #########################################################
// #             WARNING   WARNING   WARNING               #
// #########################################################
// #                                                       #
// # This file is intended for demonstration purposes      #
// # only.                                                 #
// #                                                       #
// # It is the SOLE responsibility of YOU, the programmer  #
// # to prevent against unauthorized access to any signing #
// # functions.                                            #
// #                                                       #
// # Organizations that do not protect against un-         #
// # authorized signing will be black-listed to prevent    #
// # software piracy.                                      #
// #                                                       #
// # -QZ Industries, LLC                                   #
// #                                                       #
// #########################################################

/**
 * Depends:
 *     - jsrsasign-latest-all-min.js
 *     - qz-tray.js
 *
 * Steps:
 *
 *     1. Include jsrsasign 8.0.4 into your web page
 *        <script src="https://cdn.rawgit.com/kjur/jsrsasign/c057d3447b194fa0a3fdcea110579454898e093d/jsrsasign-all-min.js"></script>
 *
 *     2. Update the privateKey below with contents from private-key.pem
 *
 *     3. Include this script into your web page
 *        <script src="path/to/sign-message.js"></script>
 *
 *     4. Remove or comment out any other references to "setSignaturePromise"
 */
var privateKey = "-----BEGIN CERTIFICATE-----\n" +
"MIIEGzCCAwOgAwIBAgIUAYBEItICB67olhVnirqzGpgrw+4wDQYJKoZIhvcNAQEL\n" +
"BQAwgZwxCzAJBgNVBAYTAklEMRAwDgYDVQQIDAdKYWthcnRhMRAwDgYDVQQHDAdK\n" +
"YWthcnRhMRIwEAYDVQQKDAlTYXR1IE1lamExFTATBgNVBAsMDFByaW50IFNlcnZl\n" +
"cjETMBEGA1UEAwwKUVogUHJpbnRlcjEpMCcGCSqGSIb3DQEJARYaZW5naW5lZXJp\n" +
"bmdAc2F0dW1lamEuY28uaWQwHhcNMjMwOTEyMTUyNjUxWhcNMjgwOTEwMTUyNjUx\n" +
"WjCBnDELMAkGA1UEBhMCSUQxEDAOBgNVBAgMB0pha2FydGExEDAOBgNVBAcMB0ph\n" +
"a2FydGExEjAQBgNVBAoMCVNhdHUgTWVqYTEVMBMGA1UECwwMUHJpbnQgU2VydmVy\n" +
"MRMwEQYDVQQDDApRWiBQcmludGVyMSkwJwYJKoZIhvcNAQkBFhplbmdpbmVlcmlu\n" +
"Z0BzYXR1bWVqYS5jby5pZDCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEB\n" +
"AMVqgqhut6kfdNh8XjZXo9ahgo2UDIhqT5XBV1nT0UIE9yZdU+tf3ZM2g2cAQq1P\n" +
"L4DLjkbZTkamTrStpBJxmz+M7fTS8apHditGo35KVo9nzBIe9vopwguwQYUn+Doh\n" +
"nQNyFSqcYCAANfAwEhEAQCc4svzE8VemnnZpm7KqMbsfEM1MAKpUXNRKep70cz0k\n" +
"19pRpTKBeU5G/4hlnbVlQK9jURR7bxJDO4Gzv4I5pZu2n+an/Z2vB7LEKBAxj/tk\n" +
"gMq6Glw+AlggNF/37U9ws4Hqnb4Lgaz69xICe+A4jhLujdVhLC28bSnli8I5IFji\n" +
"/2GAco972jVp6YNVQQnx4PsCAwEAAaNTMFEwHQYDVR0OBBYEFFO6BoArc/jBMJXt\n" +
"+inVCnGKHX9+MB8GA1UdIwQYMBaAFFO6BoArc/jBMJXt+inVCnGKHX9+MA8GA1Ud\n" +
"EwEB/wQFMAMBAf8wDQYJKoZIhvcNAQELBQADggEBAFYR5Y9dejEx3sWVyuxRH5MH\n" +
"l5e9T4Rs31z5qR0RfTGGWwG5eWFptk4t2PNhGjqGtoHQ9eEBGdpWua5MuopXdG0U\n" +
"k2YDnZpz7sXobbe5/jr4kUc0ruoulYWJkKY1ZIFCnMTXVwgbaJ/QMBqvPhuI0bod\n" +
"MOQVq9er7QlhirqE52yqvBGoVlwxH3qo/V9PdAeOJpq3TJZGIWnFXeUHV2FUCDg2\n" +
"bBXHfLg0V/h1VcD0Thr9VT7MMDgD/tzIWZP1AthfeXVGB9VKI+3Yo0vELSnZPh2B\n" +
"R8yk3oibCUUhC9UtsYYsnf04AtTIOIz9tciXZNtQtHCZ7IwJrnHrdtOr7bJSj6U=\n" +
"-----END CERTIFICATE-----";

qz.security.setSignatureAlgorithm("SHA512"); // Since 2.1
qz.security.setSignaturePromise(function(toSign) {
    return function(resolve, reject) {
        try {
            var pk = KEYUTIL.getKey(privateKey);
            var sig = new KJUR.crypto.Signature({"alg": "SHA512withRSA"});  // Use "SHA1withRSA" for QZ Tray 2.0 and older
            sig.init(pk); 
            sig.updateString(toSign);
            var hex = sig.sign();
            console.log("DEBUG: \n\n" + stob64(hextorstr(hex)));
            resolve(stob64(hextorstr(hex)));
        } catch (err) {
            console.error(err);
            reject(err);
        }
    };
});