import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

void main() => runApp(AirGuardianApp());

class AirGuardianApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Air Guardian',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: HomePage(),
    );
  }
}

enum UserType { normal, asma, epoc }

class HomePage extends StatefulWidget {
  @override
  _HomePageState createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  UserType selectedUser = UserType.normal;
  List<String> recommendations = [];
  String aqi = '';
  String nivel = '';

  final String apiBase = "http://10.0.35.80:8000/api"; // Cambia por tu IP
  final MapController _mapController = MapController();

  @override
  void initState() {
    super.initState();
    // Centrar el mapa y establecer zoom al iniciar
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _mapController.move(LatLng(19.4326, -99.1332), 10.0); // Mendex
    });
    fetchRecommendations();
    fetchAQI();
  }

  // --- Obtener recomendaciones según el tipo de usuario ---
  Future<void> fetchRecommendations() async {
    String endpoint;
    switch (selectedUser) {
      case UserType.normal:
        endpoint = "/recommendations/normal";
        break;
      case UserType.asma:
        endpoint = "/recommendations/asma";
        break;
      case UserType.epoc:
        endpoint = "/recommendations/epoc";
        break;
    }
    final response = await http.get(Uri.parse(apiBase + endpoint));
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      setState(() {
        // Tomamos solo la última recomendación
        recommendations = [data.last['Recomendación']];
      });
    }
  }

  // --- Obtener AQI actual ---
  Future<void> fetchAQI() async {
    final response = await http.get(Uri.parse(apiBase + "/aqi"));
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      setState(() {
        aqi = data['AQI'].toString();
        nivel = data['Nivel_AQI'];
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Air Guardian")),
      body: Column(
        children: [
          // --- Botones de usuario ---
          Padding(
            padding: EdgeInsets.all(8),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                ElevatedButton(
                  onPressed: () {
                    setState(() => selectedUser = UserType.normal);
                    fetchRecommendations();
                  },
                  child: Text("Personas Comunes"),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: selectedUser == UserType.normal
                        ? Colors.blue
                        : Colors.grey,
                  ),
                ),
                ElevatedButton(
                  onPressed: () {
                    setState(() => selectedUser = UserType.asma);
                    fetchRecommendations();
                  },
                  child: Text("Asma"),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: selectedUser == UserType.asma
                        ? Colors.blue
                        : Colors.grey,
                  ),
                ),
                ElevatedButton(
                  onPressed: () {
                    setState(() => selectedUser = UserType.epoc);
                    fetchRecommendations();
                  },
                  child: Text("EPOC"),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: selectedUser == UserType.epoc
                        ? Colors.blue
                        : Colors.grey,
                  ),
                ),
              ],
            ),
          ),

          // --- Mapa interactivo ---
          Expanded(
            child: FlutterMap(
              mapController: _mapController,
              options: MapOptions(
                // No center ni zoom aquí
              ),
              children: [
                TileLayer(
                  urlTemplate:
                      "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                  subdomains: ['a', 'b', 'c'],
                ),
              ],
            ),
          ),

          // --- Ventana de recomendaciones ---
          Container(
            height: 120,
            padding: EdgeInsets.all(8),
            color: Colors.grey[200],
            child: ListView.builder(
              itemCount: recommendations.length,
              itemBuilder: (context, index) {
                return Text("- ${recommendations[index]}");
              },
            ),
          ),

          // --- Índice de calidad del aire ---
          Container(
            padding: EdgeInsets.all(16),
            color: Colors.blue[50],
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text("AQI: $aqi", style: TextStyle(fontSize: 18)),
                Text("Nivel: $nivel", style: TextStyle(fontSize: 18)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
