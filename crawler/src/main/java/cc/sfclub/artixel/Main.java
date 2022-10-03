package cc.sfclub.artixel;

import javax.net.ssl.SSLParameters;
import java.net.http.HttpClient;

public class Main {
    private static final String BASE = "https://api.curseforge.com";
    private final HttpClient client = HttpClient.newBuilder()
            //  .sslParameters(prepareSSLParameter())
            .build();

    public static void main(String[] args) {
        new Main().run();
    }

    private SSLParameters prepareSSLParameter() {
        var param = new SSLParameters();
        param.setUseCipherSuitesOrder(true);
        param.setCipherSuites(TLSSuite.PREFERRED_SUITES);
        return param;
    }

    private void run() {
        new ModCrawler(System.out::println)
                .run(client);
    }


}