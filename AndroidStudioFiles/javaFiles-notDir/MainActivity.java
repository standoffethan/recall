package com.example.memory_app_bloom;

import android.os.Bundle;
import android.util.Log;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.navigation.NavController;
import androidx.navigation.fragment.NavHostFragment;
import androidx.navigation.ui.NavigationUI;

import com.google.android.material.bottomnavigation.BottomNavigationView;

public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_main);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        //Allow the user to change between fragments
        //Get a referance to the bottom navigation menu
        BottomNavigationView bnv = findViewById(R.id.bottomNav);

        //get a referance to the fragmentContainerView
        NavHostFragment nhf = (NavHostFragment) getSupportFragmentManager().findFragmentById(R.id.fragmentView);

        //get the navigation controller from the navHostFragment fragmentContainerView
        assert nhf != null;
        NavController controller = nhf.getNavController();

        //Set up the bottom navigation menu (view) to use the navigation piece
        NavigationUI.setupWithNavController(bnv, controller);
    }
}