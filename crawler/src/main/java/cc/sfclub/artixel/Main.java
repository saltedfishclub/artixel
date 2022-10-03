package cc.sfclub.artixel;

import javax.net.ssl.SSLParameters;
import java.net.http.HttpClient;
import java.nio.file.Path;
import java.util.concurrent.atomic.AtomicInteger;

public class Main {
    private static final String BASE = "https://api.curseforge.com";
    private final HttpClient client = HttpClient.newBuilder()
            //  .sslParameters(prepareSSLParameter())
            .build();
    private final AtomicInteger counter = new AtomicInteger();

    public static void main(String[] args) {
        new Main().run();
    }

    private SSLParameters prepareSSLParameter() {
        return new SSLParameters();
    }

    private void run() {
        new McModCrawler(client, Path.of("out"))
                .run();
        while (true) {
        }
    }

}