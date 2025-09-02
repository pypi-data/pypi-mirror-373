from binance.api import API


class Spot(API):
    def __init__(self, api_key=None, api_secret=None, **kwargs):
        if "base_url" not in kwargs:
            kwargs["base_url"] = "https://api.binance.com"
        super().__init__(api_key, api_secret, **kwargs)

    # Auto-Invest
    from binance.spot._auto_invest import (
        change_plan_status,
        get_index_linked_plan_redemption_history,
        get_list_of_plans,
        get_target_asset_list,
        get_target_asset_roi_data,
        index_linked_plan_rebalance_details,
        index_linked_plan_redemption,
        one_time_transaction,
        query_all_source_asset_and_target_asset,
        query_holding_details_of_the_plan,
        query_index_details,
        query_index_linked_plan_position_details,
        query_one_time_transaction_status,
        query_source_asset_list,
        query_subscription_transaction_history,
    )

    # C2C
    from binance.spot._c2c import c2c_trade_history

    # CONVERT
    from binance.spot._convert import (
        accept_quote,
        cancel_limit_order,
        get_convert_trade_history,
        list_all_convert_pairs,
        order_status,
        place_limit_order,
        query_limit_open_order,
        query_order_quantity_precision_per_asset,
        send_quote_request,
    )

    # Crypto LOANS
    from binance.spot._crypto_loan import (
        loan_adjust_ltv_history,
        loan_borrow_history,
        loan_history,
        loan_loanable_data,
        loan_repay_history,
        loan_vip_collateral_account,
        loan_vip_ongoing_orders,
        loan_vip_repay,
        loan_vip_repay_history,
    )

    # STREAMS
    from binance.spot._data_stream import (
        close_isolated_margin_listen_key,
        close_listen_key,
        close_margin_listen_key,
        new_isolated_margin_listen_key,
        new_listen_key,
        new_margin_listen_key,
        renew_isolated_margin_listen_key,
        renew_listen_key,
        renew_margin_listen_key,
    )

    # FIAT
    from binance.spot._fiat import fiat_order_history, fiat_payment_history

    # Gift Card (Binance Code in the API documentation)
    from binance.spot._gift_card import (
        gift_card_buy_code,
        gift_card_create_code,
        gift_card_redeem_code,
        gift_card_rsa_public_key,
        gift_card_token_limit,
        gift_card_verify_code,
    )

    # MARGIN
    from binance.spot._margin import (
        adjust_cross_margin_max_leverage,
        bnbBurn_status,
        borrow_repay,
        borrow_repay_record,
        cancel_isolated_margin_account,
        cancel_margin_oco_order,
        cancel_margin_order,
        cross_margin_collateral_ratio,
        enable_isolated_margin_account,
        get_a_future_hourly_interest_rate,
        get_margin_oco_order,
        get_margin_oco_orders,
        get_margin_open_oco_orders,
        get_small_liability_exchange_coin_list,
        get_small_liability_exchange_history,
        isolated_margin_account,
        isolated_margin_account_limit,
        isolated_margin_all_pairs,
        isolated_margin_fee,
        isolated_margin_tier,
        liability_coin_leverage_bracket,
        margin_account,
        margin_all_assets,
        margin_all_orders,
        margin_all_pairs,
        margin_available_inventory,
        margin_fee,
        margin_force_liquidation_record,
        margin_interest_history,
        margin_interest_rate_history,
        margin_manual_liquidation,
        margin_max_borrowable,
        margin_max_transferable,
        margin_my_trades,
        margin_new_oto_order,
        margin_new_otoco_order,
        margin_open_orders,
        margin_open_orders_cancellation,
        margin_order,
        margin_order_usage,
        margin_pair_index,
        margin_transfer_history,
        new_margin_oco_order,
        new_margin_order,
        summary_of_margin_account,
        toggle_bnbBurn,
    )

    # MARKETS
    from binance.spot._market import (
        agg_trades,
        avg_price,
        book_ticker,
        depth,
        exchange_info,
        historical_trades,
        klines,
        ping,
        rolling_window_ticker,
        ticker_24hr,
        ticker_price,
        time,
        trades,
        trading_day_ticker,
        ui_klines,
    )

    # MINING
    from binance.spot._mining import (
        mining_account_earning,
        mining_account_list,
        mining_algo_list,
        mining_bonus_list,
        mining_coin_list,
        mining_earnings_list,
        mining_hashrate_resale_cancellation,
        mining_hashrate_resale_details,
        mining_hashrate_resale_list,
        mining_hashrate_resale_request,
        mining_statistics_list,
        mining_worker,
        mining_worker_list,
    )

    # NFT
    from binance.spot._nft import (
        nft_asset,
        nft_deposit_history,
        nft_transaction_history,
        nft_withdraw_history,
    )

    # PAY
    from binance.spot._pay import pay_history

    # Portfolio Margin
    from binance.spot._portfolio_margin import (
        bnb_transfer,
        change_auto_repay_futures_status,
        fund_auto_collection,
        fund_collection_by_asset,
        get_auto_repay_futures_status,
        get_portfolio_margin_account_balance,
        get_portfolio_margin_span_account_info,
        portfolio_margin_account,
        portfolio_margin_bankruptcy_loan_amount,
        portfolio_margin_bankruptcy_loan_repay,
        portfolio_margin_collateral_rate,
        portfolio_margin_tiered_collateral_rate,
        query_classic_portfolio_margin_negative_balance_interest_history,
        query_portfolio_margin_asset_index_price,
        repay_futures_negative_balance,
    )

    # REBATE
    from binance.spot._rebate import rebate_spot_history

    # Simple Earn
    from binance.spot._simple_earn import (
        get_collateral_record,
        get_flexible_personal_left_quota,
        get_flexible_product_position,
        get_flexible_redemption_record,
        get_flexible_rewards_history,
        get_flexible_subscription_preview,
        get_flexible_subscription_record,
        get_locked_personal_left_quota,
        get_locked_product_position,
        get_locked_redemption_record,
        get_locked_rewards_history,
        get_locked_subscription_preview,
        get_locked_subscription_record,
        get_rate_history,
        get_simple_earn_flexible_product_list,
        get_simple_earn_locked_product_list,
        redeem_flexible_product,
        redeem_locked_product,
        set_flexible_auto_subscribe,
        set_locked_auto_subscribe,
        set_locked_product_redeem_option,
        simple_account,
        subscribe_flexible_product,
        subscribe_locked_product,
    )

    # Staking
    from binance.spot._staking import (
        eth_staking_account,
        get_beth_rewards_distribution_history,
        get_eth_redemption_history,
        get_eth_staking_history,
        get_eth_staking_quota,
        get_wbeth_rate_history,
        get_wbeth_rewards_history,
        get_wbeth_unwrap_history,
        get_wbeth_wrap_history,
        redeem_eth,
        subscribe_eth_staking,
        wrap_beth,
    )

    # SUB-ACCOUNT
    from binance.spot._sub_account import (
        detail_on_sub_account_s_futures_account,
        enable_options_for_sub_account,
        futures_position_risk_of_sub_account,
        managed_sub_account_assets,
        managed_sub_account_deposit,
        managed_sub_account_deposit_address,
        managed_sub_account_get_snapshot,
        managed_sub_account_investor_trans_log,
        managed_sub_account_trading_trans_log,
        managed_sub_account_withdraw,
        query_managed_sub_account_futures_asset_details,
        query_managed_sub_account_list,
        query_managed_sub_account_margin_asset_details,
        query_managed_sub_account_transfer_log,
        query_sub_account_assets,
        query_sub_account_transaction_statistics,
        sub_account_api_delete_ip,
        sub_account_api_get_ip_restriction,
        sub_account_assets,
        sub_account_create,
        sub_account_deposit_address,
        sub_account_deposit_history,
        sub_account_enable_futures,
        sub_account_enable_leverage_token,
        sub_account_enable_margin,
        sub_account_futures_account,
        sub_account_futures_account_summary,
        sub_account_futures_asset_transfer,
        sub_account_futures_asset_transfer_history,
        sub_account_futures_position_risk,
        sub_account_futures_transfer,
        sub_account_list,
        sub_account_margin_account,
        sub_account_margin_account_summary,
        sub_account_margin_transfer,
        sub_account_spot_summary,
        sub_account_spot_transfer_history,
        sub_account_status,
        sub_account_transfer_sub_account_history,
        sub_account_transfer_to_master,
        sub_account_transfer_to_sub,
        sub_account_universal_transfer,
        sub_account_universal_transfer_history,
        sub_account_update_ip_restriction,
        summary_of_sub_account_s_futures_account,
    )

    # ACCOUNT (including orders and trades)
    from binance.spot._trade import (
        account,
        cancel_and_replace,
        cancel_oco_order,
        cancel_open_orders,
        cancel_order,
        get_oco_open_orders,
        get_oco_order,
        get_oco_orders,
        get_open_orders,
        get_order,
        get_order_rate_limit,
        get_orders,
        my_trades,
        new_oco_order,
        new_order,
        new_order_test,
        new_oto_order,
        new_otoco_order,
        query_allocations,
        query_commission_rates,
        query_prevented_matches,
    )

    # WALLET
    from binance.spot._wallet import (
        account_snapshot,
        account_status,
        api_key_permissions,
        api_trading_status,
        asset_detail,
        asset_dividend_record,
        balance,
        bnb_convertible_assets,
        cloud_mining_trans_history,
        coin_info,
        delist_schedule_symbols,
        deposit_address,
        deposit_history,
        disable_fast_withdraw,
        dust_log,
        enable_fast_withdraw,
        funding_wallet,
        list_deposit_address,
        local_entity_deposit_history,
        local_entity_submit_deposit_questionnaire,
        local_entity_withdraw,
        local_entity_withdraw_history,
        one_click_arrival_deposit_apply,
        system_status,
        trade_fee,
        transfer_dust,
        user_asset,
        user_universal_transfer,
        user_universal_transfer_history,
        withdraw,
        withdraw_history,
    )
