package com.example.memory_app_bloom;

import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.widget.TextView;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

public class PlayingActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_playing);

        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        final String[] data = {""};
        final JSONObject[] json = new JSONObject[1];

        Handler mainHandler = new Handler(Looper.getMainLooper());

        // TODO: Replace this with your actual input string
        final String urlQuerry = "http://10.2.2"; //put ?<len> to specify text length

        new Thread(new Runnable() {
            @Override
            public void run() {
                String data = doWebApiCall(urlQuerry);

                // Run UI updates on main thread
                mainHandler.post(new Runnable() {
                    @Override
                    public void run() {
                        // TODO: Replace this with your actual UI update
                        TextView reading = findViewById(R.id.reading);
                        reading.setText(data);
                    }
                });
            }
        }).start();
    }

    String doWebApiCall(String urlQuerry) {
        try {
            URL url = new URL(urlQuerry);
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("GET");
            connection.setConnectTimeout(5000);
            connection.setReadTimeout(5000);
            connection.connect();

            InputStream stream = connection.getInputStream();
            BufferedReader br = new BufferedReader(new InputStreamReader(stream));

            String line;
            StringBuilder data = new StringBuilder();

            while ((line = br.readLine()) != null) {
                data.append(line);
            }

            JSONObject jo = new JSONObject(data.toString());
            return data.toString();

        } catch (Exception e) {
            Log.e("Error in webAPICall", e.toString());
        }
        return "";
    }
}
