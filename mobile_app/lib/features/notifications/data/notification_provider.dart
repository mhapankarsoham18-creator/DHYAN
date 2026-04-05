import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile_app/core/network/dio_client.dart';

class NotificationModel {
  final String id;
  final String type;
  final String title;
  final String message;
  final bool isRead;
  final String createdAt;

  NotificationModel({
    required this.id,
    required this.type,
    required this.title,
    required this.message,
    required this.isRead,
    required this.createdAt,
  });

  factory NotificationModel.fromJson(Map<String, dynamic> json) {
    return NotificationModel(
      id: json['id'] as String,
      type: json['type'] as String,
      title: json['title'] as String,
      message: json['message'] as String,
      isRead: json['is_read'] as bool,
      createdAt: json['created_at'] as String,
    );
  }
}

class NotificationsNotifier extends StateNotifier<AsyncValue<List<NotificationModel>>> {
  NotificationsNotifier() : super(const AsyncValue.loading()) {
    fetchNotifications();
  }

  Future<void> fetchNotifications() async {
    try {
      state = const AsyncValue.loading();
      final response = await dioClient.dio.get('/api/v1/notifications/');
      final data = response.data['notifications'] as List;
      final notifications = data.map((n) => NotificationModel.fromJson(n)).toList();
      state = AsyncValue.data(notifications);
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
    }
  }

  Future<void> markAsRead(String id) async {
    try {
      await dioClient.dio.patch('/api/v1/notifications/$id/read');
      
      // Optimistically update local state
      state = state.whenData((notifications) {
        return notifications.map((n) {
          if (n.id == id) {
            return NotificationModel(
              id: n.id,
              type: n.type,
              title: n.title,
              message: n.message,
              isRead: true,
              createdAt: n.createdAt,
            );
          }
          return n;
        }).toList();
      });
    } catch (e) {
      // Revert or log error
    }
  }

  Future<void> markAllAsRead() async {
    try {
      await dioClient.dio.post('/api/v1/notifications/mark-all-read');
      
      // Optimistically update local state
      state = state.whenData((notifications) {
        return notifications.map((n) {
          return NotificationModel(
            id: n.id,
            type: n.type,
            title: n.title,
            message: n.message,
            isRead: true,
            createdAt: n.createdAt,
          );
        }).toList();
      });
    } catch (e) {
      // Revert or log error
    }
  }
}

final notificationsProvider = StateNotifierProvider<NotificationsNotifier, AsyncValue<List<NotificationModel>>>(
  (ref) => NotificationsNotifier(),
);
