qz.security.setCertificatePromise(function (resolve, reject) {
    resolve("-----BEGIN CERTIFICATE-----\n" +
            "MIID5TCCAs2gAwIBAgIJALzQm+/XXbwMMA0GCSqGSIb3DQEBCwUAMIGIMQswCQYDVQQGEwJMSzEQMA4GA1UECAwHV2VzdGVybjEQMA4GA1UEBwwHQ29sb21ibzEQMA4GA1UECgwHTWVlcHVyYTELMAkGA1UECwwCSVQxEjAQBgNVBAMMCWxvY2FsaG9zdDEiMCAGCSqGSIb3DQEJARYTOTJidWRkaGl2QGdtYWlsLmNvbTAeFw0xNzA1MDQxMjM4MjZaFw00ODEwMjcxMjM4MjZaMIGIMQswCQYDVQQGEwJMSzEQMA4GA1UECAwHV2VzdGVybjEQMA4GA1UEBwwHQ29sb21ibzEQMA4GA1UECgwHTWVlcHVyYTELMAkGA1UECwwCSVQxEjAQBgNVBAMMCWxvY2FsaG9zdDEiMCAGCSqGSIb3DQEJARYTOTJidWRkaGl2QGdtYWlsLmNvbTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAOiWVtI4eLVNMVCLgb9GJrRTBhiTxZ7KtC/4ydIh4ZNyb5vy9ykfzFHbLQKsfvbPArJdlEHkl5vu+gCV9i8B1wsF2bH/GUwtUFshzkV58w2PQByIfeh/G5YtHV2N8LLy7W/4QRWClN7HtGHyIJBG5WkrXHJRAzxsX4BzEgQZA4gXGagOxhamWSs2XGnIdP7IqeLe0xFz+1m0cwuVDIkJbUnKYGQjLlX1Xo8tstrgcerZmXrcWcqIXswtN4Mm9azmigpmHHGGzynqqaP4i8VSOpwSS62Mz0YEb2Y4+Y9zPvs7UOX3aJY/LiXjYMcWrNulU3/O4utvJiGT0/L+ILVfXgkCAwEAAaNQME4wHQYDVR0OBBYEFNKWk9dscGiV2CLFMMrteh8tvmNzMB8GA1UdIwQYMBaAFNKWk9dscGiV2CLFMMrteh8tvmNzMAwGA1UdEwQFMAMBAf8wDQYJKoZIhvcNAQELBQADggEBAK/iPW5iTcVJNd44g2Uc+IV7XPCIY6fi+Hv3+0LbEhtThmQOGi2Zf2yv9BiMP8eVuhew3ovqlgXVQqgq+WM+Dweba7vEhGpadltYNPlrbpLi1PMEIi1rdJ4AN4ALwmWSpqUucU3/Z4B+fJVuJ/z+XkR7tzaJzsQcjLK/NZhxj26Yl2KwthWRpXzq3ZSTMP1Jqv7C0nI597lTV+C3yObY/JfxE0blUSv0DZrg8JrHeTgW9fd3+4+UhRtX7YW+SYpOCbZP/HrCQumCwRkZ7xb3Rbp8vp3ol40p+ka5BBEBADhVjUfq649O66o9M3HCfkUYQ+lIhjNkMOMoD0H9pP7wXE4=\n" +
            "-----END CERTIFICATE-----");
});

var privateKey = "-----BEGIN PRIVATE KEY-----\n" +
        "MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDollbSOHi1TTFQi4G/Ria0UwYYk8WeyrQv+MnSIeGTcm+b8vcpH8xR2y0CrH72zwKyXZRB5Jeb7voAlfYvAdcLBdmx/xlMLVBbIc5FefMNj0AciH3ofxuWLR1djfCy8u1v+EEVgpTex7Rh8iCQRuVpK1xyUQM8bF+AcxIEGQOIFxmoDsYWplkrNlxpyHT+yKni3tMRc/tZtHMLlQyJCW1JymBkIy5V9V6PLbLa4HHq2Zl63FnKiF7MLTeDJvWs5ooKZhxxhs8p6qmj+IvFUjqcEkutjM9GBG9mOPmPcz77O1Dl92iWPy4l42DHFqzbpVN/zuLrbyYhk9Py/iC1X14JAgMBAAECggEBAKMRJHXm2dpi8HxEEweDq4cp3lBE6nzWKVao2vbUgk7aIJ35zoeqn5mUTQ5e2fU4Ve+v5E3+cr0E44qdmSiD5bz4sRQ2ggoCiyAZp4DWay3KjWxz1bK3yyOTJc99wI/1+bpTF255St6WrUUueN4ulpERsZMEcXxfjuWDx9HPp8Y09YYgfxW+VFioFCdjlnMMRBBqWYbRS8FwU11k+Ai9sfHPhdCcPtLAF2V2brgpOonZtjuCo7nwsQs6Q33VToWj64xE7fPlAvVPouSH4hp93iv/ULSvBWT6w/wmjWckGEinDg49/GuRv3XRZ5FFmWnWugwmLQTpRyNJEi1J7lCEPfECgYEA/UbP/GJOSr1clm3AGQPrmcxTU0nV9Hvrc1pt/2L0aPTU7h95/mJ2Ue4f8kVZBogp6gU9LZQdP37Mz41MgZWLreMUyQSdI9KZH3G6uVRc/LNg5xDET70uyeun+dw1Io+5e6rlGaHVKERYoeSgTTI+eeZCJNoOi5hhPKbq5wJRlsMCgYEA6xaTYQlhNEx8b1ElAklAMjn9FJPJVirOKijfFOrE7ZpTvaOQ1PDC2paXY9ZcA3LMNgnGT7BSJS+sUc627XHYUuo6mp/0ILsq+9qvth/tDyR0tENIrRCfZZGBxM+avC8/1C0TXQIyeB8uLxR89JSQQhVH3zwQjUXH92GrcP/y40MCgYEA+hyJm0RA6FGjMvHid1GFwXUi++a4IByXYGx2n3JKxbKw6w2uXOVCzpmGdqrAxVCFg5H03iOb1m4TNwrj+DuDmg3bIr8ppox7pa+boxSKVwmUsdm+4reBkujiEj3BQwYHNvaGEw/a/U6w7/5jxpfNVndp7hZfsr6hl1GGOuXxSB0CgYEAluYX1dqidWJ/ISjx24TPWy4TwCiYvOGfEjrH7vI/U9CS3hBmv/iG6q5tIJ2Q1HnUkP83NyGTqODv+Fb63nEMDTTiRyxTFMtvbNhTn1Dg5q5c5vSlaslXt2dt57nmtdKSYwxH+JSXdrl0+K1rA8d0zaZBSw6QBU58a9Naq57u9mcCgYAanz5/Rw1VUbcViRMVueuopdPo6hgNv/9ciBsgOqhxq6srtoPcFEo3fNU5v5pdKQGaI8hfkjMhR4sYw3JbWcB7JIJTtjCJvUuDUJNrf62+couuCX7WQUrBq7HVOtaFD92P86d6JGqjNYSYMarSAlMCgd0TtJKPK/gu7xDNhdWahQ==\n" +
        "-----END PRIVATE KEY-----";

qz.security.setSignaturePromise(function (toSign) {
    return function (resolve, reject) {
        try {
            var pk = new RSAKey();
            pk.readPrivateKeyFromPEMString(strip(privateKey));
            var hex = pk.signString(toSign, 'sha1');
            console.log("DEBUG: \n\n" + stob64(hextorstr(hex)));
            resolve(stob64(hextorstr(hex)));
        } catch (err) {
            console.error(err);
            reject(err);
        }
    };
});

function strip(key) {
    if (key.indexOf('-----') !== -1) {
        return key.split('-----')[2].replace(/\r?\n|\r/g, '');
    }
}