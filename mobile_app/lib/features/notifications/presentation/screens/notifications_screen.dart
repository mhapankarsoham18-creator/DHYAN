import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile_app/core/theme/app_theme.dart';
import 'package:mobile_app/features/notifications/data/notification_provider.dart';

class NotificationsScreen extends ConsumerStatefulWidget {
  const NotificationsScreen({super.key});

  @override
  ConsumerState<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends ConsumerState<NotificationsScreen> {

  @override
  Widget build(BuildContext context) {
    final notificationsState = ref.watch(notificationsProvider);

    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        leading: IconButton(
          onPressed: () => Scaffold.of(context).openDrawer(),
          icon: const Icon(Icons.menu_rounded, size: 22),
        ),
        title: const Text('Notifications'),
        actions: [
          TextButton(
            onPressed: () {
              ref.read(notificationsProvider.notifier).markAllAsRead();
            },
            child: Text(
              'Mark all read',
              style: AppTheme.bodySmall.copyWith(color: AppTheme.primary, fontWeight: FontWeight.w600),
            ),
          ),
        ],
      ),
      body: notificationsState.when(
        data: (notifications) {
          if (notifications.isEmpty) {
            return Center(
              child: Text(
                'No new notifications',
                style: AppTheme.bodyMedium.copyWith(color: AppTheme.textTertiary),
              ),
            );
          }

          return RefreshIndicator(
            onRefresh: () => ref.read(notificationsProvider.notifier).fetchNotifications(),
            color: AppTheme.primary,
            child: ListView.builder(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
              physics: const AlwaysScrollableScrollPhysics(parent: BouncingScrollPhysics()),
              itemCount: notifications.length + 2, // +2 for header and footer
              itemBuilder: (context, index) {
                if (index == 0) {
                  return _buildDateHeader('Recent');
                }
                if (index == notifications.length + 1) {
                  return const Padding(
                    padding: EdgeInsets.only(top: 48, bottom: 24),
                    child: Center(
                      child: Text(
                        'Only showing last 30 notifications',
                        style: TextStyle(fontSize: 11, color: AppTheme.textTertiary),
                      ),
                    ),
                  );
                }

                final n = notifications[index - 1];
                IconData icon;
                Color iconColor;

                switch (n.type) {
                  case 'ALERT':
                    icon = Icons.trending_up_rounded;
                    iconColor = AppTheme.success;
                    break;
                  case 'ORDER':
                    icon = Icons.check_circle_rounded;
                    iconColor = AppTheme.primary;
                    break;
                  case 'TRANSACTION':
                    icon = Icons.account_balance_wallet_rounded;
                    iconColor = AppTheme.accent;
                    break;
                  default:
                    icon = Icons.info_rounded;
                    iconColor = AppTheme.info;
                }

                return GestureDetector(
                  onTap: () {
                    if (!n.isRead) {
                      ref.read(notificationsProvider.notifier).markAsRead(n.id);
                    }
                  },
                  child: _buildNotificationCard(
                    icon: icon,
                    iconColor: iconColor,
                    title: n.title,
                    body: n.message,
                    time: n.createdAt.length >= 10 ? n.createdAt.substring(0, 10) : n.createdAt,
                    isUnread: !n.isRead,
                    dimmed: n.isRead,
                  ),
                );
              },
            ),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator(color: AppTheme.primary)),
        error: (err, _) => Center(
          child: Text(
            'Failed to load notifications: \n${err.toString()}',
            textAlign: TextAlign.center,
            style: AppTheme.bodyMedium.copyWith(color: AppTheme.danger),
          ),
        ),
      ),
    );
  }

  Widget _buildDateHeader(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12, top: 4),
      child: Text(
        title,
        style: AppTheme.labelMedium.copyWith(
          fontSize: 11,
          letterSpacing: 1.5,
          color: AppTheme.textTertiary,
        ),
      ),
    );
  }

  Widget _buildNotificationCard({
    required IconData icon,
    required Color iconColor,
    required String title,
    required String body,
    required String time,
    required bool isUnread,
    bool dimmed = false,
  }) {
    return Opacity(
      opacity: dimmed ? 0.6 : 1.0,
      child: Container(
        margin: const EdgeInsets.only(bottom: 8),
        padding: const EdgeInsets.all(16),
        decoration: AppTheme.premiumCard(),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Icon with glow
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: iconColor.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(icon, color: iconColor, size: 20),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          title,
                          style: TextStyle(
                            color: AppTheme.textPrimary,
                            fontWeight: isUnread ? FontWeight.w600 : FontWeight.w400,
                            fontSize: 14,
                          ),
                        ),
                      ),
                      if (isUnread)
                        Container(
                          width: 7,
                          height: 7,
                          decoration: const BoxDecoration(
                            color: AppTheme.primary,
                            shape: BoxShape.circle,
                          ),
                        ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(body, style: AppTheme.bodySmall.copyWith(fontSize: 12, color: AppTheme.textSecondary)),
                  const SizedBox(height: 6),
                  Text(time, style: AppTheme.bodySmall.copyWith(fontSize: 10)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
