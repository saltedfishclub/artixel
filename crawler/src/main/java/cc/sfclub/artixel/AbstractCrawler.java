package cc.sfclub.artixel;

import lombok.RequiredArgsConstructor;

import java.net.URI;
import java.net.http.HttpRequest;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;

@RequiredArgsConstructor
public abstract class AbstractCrawler {
    public static final ScheduledExecutorService SCHEDULER = Executors.newScheduledThreadPool(2);
    protected final String baseUrl;

    public abstract void run();

    protected HttpRequest.Builder withHeader(String path) {
        return HttpRequest.newBuilder(URI.create(baseUrl + path))
                //.header("x-api-key", apiKey)
                .header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; rv:105.0) Gecko/20100101 Firefox/105.0");
        //.header("Connection","keep-alive")
        ///  .header("Host","www.curseforge.com");
    }
}
