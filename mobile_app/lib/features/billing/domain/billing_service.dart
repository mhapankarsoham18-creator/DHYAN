import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_dotenv/flutter_dotenv.dart';

class BillingService {
  final String _baseUrl = dotenv.env['API_URL'] ?? 'http://192.168.0.104:8000/api/v1';

  Future<Map<String, dynamic>> createSubscription(String jwtToken) async {
    final response = await http.post(
      Uri.parse('$_baseUrl/billing/create-subscription'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $jwtToken',
      },
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to create subscription: ${response.body}');
    }
  }

  Future<Map<String, dynamic>> checkSubscriptionStatus(String jwtToken) async {
    final response = await http.get(
      Uri.parse('$_baseUrl/billing/status'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $jwtToken',
      },
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get subscription status: ${response.body}');
    }
  }
}
