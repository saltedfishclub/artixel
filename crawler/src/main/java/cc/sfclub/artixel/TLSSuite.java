package cc.sfclub.artixel;

public class TLSSuite {
    public static final String[] PREFERRED_SUITES = new String[]{
            "TLS_RSA_WITH_AES_256_GCM_SHA384"
//            "TLS_AES_256_GCM_SHA384",
/*            "TLS_AES_128_GCM_SHA256",
            "TLS_CHACHA20_POLY1305_SHA256",
            "TLS_AES_256_GCM_SHA384",
            "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
            "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
            "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256",
            "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256",
            "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
            "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
            "TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA",
            "TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA",
            "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA",
            "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA",
            "TLS_RSA_WITH_AES_128_GCM_SHA256",
            "TLS_RSA_WITH_AES_256_GCM_SHA384",
            "TLS_RSA_WITH_AES_128_CBC_SHA",
            "TLS_RSA_WITH_AES_256_CBC_SHA"*/
    };
    public static final String[] PREFERRED_CURVES = new String[]{
            "x25519",
            "secp256r1",
            "secp384r1",
            "secp521r1",
            "ffdhe2048",
            "ffdhe3072"
    };
    public static final String[] TLS_EXTENSIONS = new String[]{
            "server_name",
            "extended_master_secret",
            "renegotiation_info",
            "supported_groups",
            "ec_point_formats",
            "application_layer_protocol_negotiation",
            "status_request",
            "key_share",
            "supported_versions",
            "signature_algorithms",
            "psk_key_exchange_modes",
            "record_size_limit",
            "padding",
            "pre_shared_key"
    };
}
