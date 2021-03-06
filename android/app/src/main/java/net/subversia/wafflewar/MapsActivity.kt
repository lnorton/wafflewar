package net.subversia.wafflewar

import android.content.Context
import android.graphics.Color
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle

import com.google.android.gms.maps.CameraUpdateFactory
import com.google.android.gms.maps.GoogleMap
import com.google.android.gms.maps.OnMapReadyCallback
import com.google.android.gms.maps.SupportMapFragment
import com.google.android.gms.maps.model.LatLng
import com.google.android.gms.maps.model.PolygonOptions

import org.json.JSONArray

import java.io.BufferedReader

class MapsActivity : AppCompatActivity(), OnMapReadyCallback {

    private lateinit var mMap: GoogleMap

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_maps)
        // Obtain the SupportMapFragment and get notified when the map is ready to be used.
        val mapFragment = supportFragmentManager.findFragmentById(R.id.map) as SupportMapFragment
        mapFragment.getMapAsync(this)
    }

    /**
     * Manipulates the map once available.
     * This callback is triggered when the map is ready to be used.
     * This is where we can add markers or lines, add listeners or move the camera. In this case,
     * we just add a marker near Sydney, Australia.
     * If Google Play services is not installed on the device, the user will be prompted to install
     * it inside the SupportMapFragment. This method will only be triggered once the user has
     * installed Google Play services and returned to the app.
     */
    override fun onMapReady(googleMap: GoogleMap) {
        mMap = googleMap

        loadAllTheHouses(googleMap)

        googleMap.moveCamera(CameraUpdateFactory.newLatLng(LatLng(33.77555534, -84.27381381)))
    }

    private fun loadAllTheHouses(googleMap: GoogleMap) {
        val houses = JSONArray(loadStringAsset(this, "houses.json"))
        for (i in 0 until houses.length()) {
            val shop = houses.getJSONObject(i)
            val house = shop.getString("house")
            val coords = shop.getJSONArray("coords")
            val region = shop.getJSONArray("region")
            var fillColor = when (house) {
                "WH" -> Color.YELLOW
                "HH" -> Color.rgb(255, 165, 0) // Orange
                "IHOP" -> Color.BLUE
                else -> Color.GREEN
            }
            fillColor = Color.argb(128, Color.red(fillColor), Color.green(fillColor), Color.blue(fillColor))
            val polygonOptions = PolygonOptions()
            polygonOptions.fillColor(fillColor)
            polygonOptions.strokeColor(Color.GRAY)
            polygonOptions.strokeWidth(1.0f)
            for (j in 0 until region.length()) {
                val point = region.getJSONArray(j)
                polygonOptions.add(LatLng(point.getDouble(0), point.getDouble(1)))
            }
            googleMap.addPolygon(polygonOptions)
        }
    }

    private fun loadStringAsset(context: Context, filename: String): String {
        return context.assets.open(filename).bufferedReader().use(BufferedReader::readText)
    }
}