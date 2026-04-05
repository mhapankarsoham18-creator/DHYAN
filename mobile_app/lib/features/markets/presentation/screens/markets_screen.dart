import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile_app/core/theme/app_theme.dart';
import '../controllers/markets_controller.dart';

class MarketsScreen extends ConsumerStatefulWidget {
  const MarketsScreen({super.key});

  @override
  ConsumerState<MarketsScreen> createState() => _MarketsScreenState();
}

class _MarketsScreenState extends ConsumerState<MarketsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this); 
  }

  @override
  void dispose() {
    _tabController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final stateAsync = ref.watch(marketsControllerProvider);
    final notifier = ref.read(marketsControllerProvider.notifier);
    
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: Row(
          children: [
            const Text('Markets', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 22)),
            const Spacer(),
            if (stateAsync.value != null)
               _buildMarketStatusBadge(stateAsync.value!.isMarketOpen),
          ],
        ),
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: AppTheme.primary,
          labelColor: AppTheme.primary,
          unselectedLabelColor: AppTheme.textSecondary,
          labelStyle: const TextStyle(fontWeight: FontWeight.bold),
          dividerColor: AppTheme.surfaceVariant,
          tabs: const [
            Tab(text: 'Overview (Indices)'),
            Tab(text: 'Movers (Gainers/Losers)'),
          ],
        ),
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: TextField(
              controller: _searchController,
              style: const TextStyle(color: AppTheme.textPrimary),
              decoration: InputDecoration(
                hintText: 'Search Stocks, ETFs, Indices...',
                hintStyle: const TextStyle(color: AppTheme.textSecondary),
                prefixIcon: const Icon(
                  Icons.search,
                  color: AppTheme.textSecondary,
                ),
                filled: true,
                fillColor: AppTheme.surface,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(16),
                  borderSide: BorderSide.none,
                ),
                contentPadding: const EdgeInsets.symmetric(vertical: 14),
              ),
            ),
          ),
          
          if (stateAsync.value?.errorText != null) 
             Container(
               width: double.infinity,
               color: AppTheme.danger.withValues(alpha: 0.1),
               padding: const EdgeInsets.all(8),
               child: Text(
                 stateAsync.value!.errorText!,
                 textAlign: TextAlign.center,
                 style: const TextStyle(color: AppTheme.danger, fontSize: 12, fontWeight: FontWeight.bold),
               ),
             ),

          Expanded(
            child: RefreshIndicator(
              onRefresh: notifier.refresh,
              color: AppTheme.primary,
              backgroundColor: AppTheme.surface,
              child: stateAsync.when(
                loading: () => const Center(child: CircularProgressIndicator(color: AppTheme.primary)),
                error: (e, st) => const Center(child: Text('Failed to load markets.', style: TextStyle(color: AppTheme.danger))),
                data: (data) => TabBarView(
                  controller: _tabController,
                  children: [
                    _buildOverviewTab(data),
                    _buildMoversTab(data),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildMarketStatusBadge(bool isOpen) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: isOpen ? AppTheme.success.withValues(alpha: 0.15) : AppTheme.surfaceVariant,
        borderRadius: BorderRadius.circular(30),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: isOpen ? AppTheme.success : AppTheme.textSecondary,
            ),
          ),
          const SizedBox(width: 6),
          Text(
            isOpen ? 'MARKET OPEN' : 'CLOSED',
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.bold,
              letterSpacing: 0.5,
              color: isOpen ? AppTheme.success : AppTheme.textSecondary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildOverviewTab(MarketsState data) {
    if (data.indices.isEmpty) {
       return const Center(child: Text("No indices to display", style: TextStyle(color: AppTheme.textSecondary)));
    }
    
    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      itemCount: data.indices.length,
      itemBuilder: (context, index) {
        final item = data.indices[index];
        final isPositive = item.change >= 0;
        
        return Container(
          margin: const EdgeInsets.only(bottom: 12),
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: AppTheme.surface,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: AppTheme.surfaceVariant),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.05),
                blurRadius: 10, 
                offset: const Offset(0, 4)
              ),
            ],
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                item.symbol,
                style: const TextStyle(
                  color: AppTheme.textPrimary,
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    item.latestPrice.toStringAsFixed(2),
                    style: const TextStyle(
                      color: AppTheme.textPrimary,
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      Icon(
                        isPositive ? Icons.arrow_upward_rounded : Icons.arrow_downward_rounded,
                        color: isPositive ? AppTheme.success : AppTheme.danger,
                        size: 14,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        '${isPositive ? '+' : ''}${item.change.toStringAsFixed(2)} (${item.changePercent.toStringAsFixed(2)}%)',
                        style: TextStyle(
                          color: isPositive ? AppTheme.success : AppTheme.danger,
                          fontSize: 13,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildMoversTab(MarketsState data) {
    return ListView(
      padding: const EdgeInsets.all(16),
      physics: const BouncingScrollPhysics(),
      children: [
        if (data.topGainers.isNotEmpty) ...[
          const Text('Top Gainers', style: TextStyle(color: AppTheme.success, fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          _buildMoversList(data.topGainers, true),
          const SizedBox(height: 24),
        ],
        
        if (data.topLosers.isNotEmpty) ...[
          const Text('Top Losers', style: TextStyle(color: AppTheme.danger, fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          _buildMoversList(data.topLosers, false),
          const SizedBox(height: 24),
        ],
      ],
    );
  }
  
  Widget _buildMoversList(List<MarketIndex> list, bool isGainer) {
    return Column(
      children: list.map((item) {
        return Container(
          margin: const EdgeInsets.only(bottom: 12),
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
          decoration: BoxDecoration(
            color: AppTheme.surface,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppTheme.surfaceVariant),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                item.symbol,
                style: const TextStyle(
                  color: AppTheme.textPrimary,
                  fontWeight: FontWeight.bold,
                  fontSize: 15,
                ),
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    '₹${item.latestPrice.toStringAsFixed(2)}',
                    style: const TextStyle(
                      color: AppTheme.textPrimary,
                      fontWeight: FontWeight.bold,
                      fontSize: 15,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: (isGainer ? AppTheme.success : AppTheme.danger).withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      '${isGainer ? '+' : ''}${item.changePercent.toStringAsFixed(2)}%',
                      style: TextStyle(
                        color: isGainer ? AppTheme.success : AppTheme.danger,
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        );
      }).toList(),
    );
  }
}
