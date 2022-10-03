package cc.sfclub.artixel;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import lombok.SneakyThrows;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.regex.Pattern;

public class Main {

    private static final Pattern NUMBER = Pattern.compile("\\d+");
    private JsonObject lang;
    private Path target;
    private int i;

    @SneakyThrows
    public static void main(String[] args) throws IOException {
        new Main().run(args);
    }

    private void run(String[] args) throws IOException, InterruptedException {
        if (args.length != 2) {
            System.out.println("A <language file> and a <target> excepted.");
            return;
        }
        var langFile = Files.readString(Path.of(args[0]));
        target = Path.of(args[1]);
        target.toFile().mkdirs();
        System.out.println("Parsing...");
        lang = JsonParser.parseString(langFile).getAsJsonObject();
        System.out.println("Walking...");
        // start walking
        try (var walker = Files.walk(Path.of("resources"))) {
            walker
                    .filter(it -> it.toAbsolutePath().toString().endsWith(".png"))
                    .filter(it -> it.toFile().isFile())
                    .forEach(it -> generateResource(it, lang, target));
        }
        System.out.println("Waiting...");
        Thread.sleep(100);
        while (true) {
            Thread.yield();
        }
    }

    @SneakyThrows
    private void generateResource(Path path, JsonObject lang, Path target) {
        i++;
        var name = path.toFile().getName();
        var namespace = path.getParent().toFile().getName();
        name = name.substring(0, name.length() - 4);
        // split
        var sp = name.split("_");
        Files.copy(path, target.resolve(i + ".jpg"));
        if (sp.length != 0) {
            if (NUMBER.matcher(sp[sp.length - 1]).matches()) {
                String[] newArr = Arrays.copyOf(sp, sp.length - 1);
                var realName = String.join("_", newArr);
                save(lang, namespace, realName);
                return;
            }
        }
        save(lang, namespace, name);
    }

    @SneakyThrows
    private void save(JsonObject lang, String namespace, String name) {
        var ele = lang.get("item." + namespace + "." + name);
        if (ele == null) {
            System.err.println("Cannot find name for: " + namespace + ":" + name);
        }
        String keyName = ele == null ? name.replaceAll("_", " ") : ele.getAsString();
        Files.writeString(target.resolve(i + ".txt"), keyName);
    }
}