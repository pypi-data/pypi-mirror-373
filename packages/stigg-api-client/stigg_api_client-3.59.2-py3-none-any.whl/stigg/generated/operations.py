import sgqlc.types
import sgqlc.operation
from . import schema

_schema = schema
_schema_root = _schema.schema

__all__ = ('Operations',)


def fragment_coupon_fragment():
    _frag = sgqlc.operation.Fragment(_schema.Coupon, 'CouponFragment')
    _frag.id()
    _frag.discount_value()
    _frag.percent_off()
    _frag_amounts_off = _frag.amounts_off()
    _frag_amounts_off.amount()
    _frag_amounts_off.currency()
    _frag.type()
    _frag.additional_meta_data()
    _frag.ref_id()
    _frag.name()
    _frag.description()
    _frag.created_at()
    _frag.updated_at()
    _frag.billing_id()
    _frag.billing_link_url()
    _frag.status()
    _frag_sync_states = _frag.sync_states()
    _frag_sync_states.vendor_identifier()
    _frag_sync_states.status()
    return _frag


def fragment_price_tier_fragment():
    _frag = sgqlc.operation.Fragment(_schema.PriceTier, 'PriceTierFragment')
    _frag.up_to()
    _frag_unit_price = _frag.unit_price()
    _frag_unit_price.amount()
    _frag_unit_price.currency()
    _frag_flat_price = _frag.flat_price()
    _frag_flat_price.amount()
    _frag_flat_price.currency()
    return _frag


def fragment_price_fragment():
    _frag = sgqlc.operation.Fragment(_schema.Price, 'PriceFragment')
    _frag.billing_model()
    _frag.billing_period()
    _frag.billing_cadence()
    _frag.billing_id()
    _frag.min_unit_quantity()
    _frag.max_unit_quantity()
    _frag.billing_country_code()
    _frag_price = _frag.price()
    _frag_price.amount()
    _frag_price.currency()
    _frag_credit_rate = _frag.credit_rate()
    _frag_credit_rate.amount()
    _frag_credit_rate.custom_currency_id()
    _frag.tiers_mode()
    _frag_tiers = _frag.tiers()
    _frag_tiers.__fragment__(fragment_price_tier_fragment())
    _frag_feature = _frag.feature()
    _frag_feature.ref_id()
    _frag_feature.feature_units()
    _frag_feature.feature_units_plural()
    _frag_feature.display_name()
    _frag_feature.description()
    _frag.block_size()
    return _frag


def fragment_overage_price_fragment():
    _frag = sgqlc.operation.Fragment(_schema.Price, 'OveragePriceFragment')
    _frag.billing_model()
    _frag.billing_period()
    _frag.billing_id()
    _frag.billing_country_code()
    _frag_price = _frag.price()
    _frag_price.amount()
    _frag_price.currency()
    _frag.tiers_mode()
    _frag_tiers = _frag.tiers()
    _frag_tiers.__fragment__(fragment_price_tier_fragment())
    _frag_feature = _frag.feature()
    _frag_feature.ref_id()
    _frag_feature.feature_units()
    _frag_feature.feature_units_plural()
    _frag_feature.display_name()
    _frag_feature.description()
    return _frag


def fragment_total_price_fragment():
    _frag = sgqlc.operation.Fragment(_schema.CustomerSubscriptionTotalPrice, 'TotalPriceFragment')
    _frag_sub_total = _frag.sub_total()
    _frag_sub_total.amount()
    _frag_sub_total.currency()
    _frag_total = _frag.total()
    _frag_total.amount()
    _frag_total.currency()
    return _frag


def fragment_package_entitlement_fragment():
    _frag = sgqlc.operation.Fragment(_schema.PackageEntitlement, 'PackageEntitlementFragment')
    _frag.usage_limit()
    _frag.has_unlimited_usage()
    _frag.has_soft_limit()
    _frag.feature_id()
    _frag.reset_period()
    _frag.hidden_from_widgets()
    _frag.is_custom()
    _frag.display_name_override()
    _frag.enum_values()
    _frag.is_granted()
    _frag_feature = _frag.feature()
    _frag_feature.feature_type()
    _frag_feature.meter_type()
    _frag_feature.feature_units()
    _frag_feature.feature_units_plural()
    _frag_feature.display_name()
    _frag_feature.description()
    _frag_feature.ref_id()
    _frag_feature.additional_meta_data()
    return _frag


def fragment_addon_fragment():
    _frag = sgqlc.operation.Fragment(_schema.Addon, 'AddonFragment')
    _frag.id()
    _frag.ref_id()
    _frag.billing_id()
    _frag.display_name()
    _frag.description()
    _frag.additional_meta_data()
    _frag.hidden_from_widgets()
    _frag_entitlements = _frag.entitlements()
    _frag_entitlements.__fragment__(fragment_package_entitlement_fragment())
    _frag_prices = _frag.prices()
    _frag_prices.__fragment__(fragment_price_fragment())
    _frag_overage_prices = _frag.overage_prices()
    _frag_overage_prices.__fragment__(fragment_overage_price_fragment())
    _frag.pricing_type()
    _frag.max_quantity()
    _frag_dependencies = _frag.dependencies()
    _frag_dependencies.__fragment__(fragment_addon_dependency_fragment())
    return _frag


def fragment_addon_dependency_fragment():
    _frag = sgqlc.operation.Fragment(_schema.Addon, 'AddonDependencyFragment')
    _frag.id()
    _frag.ref_id()
    _frag.display_name()
    _frag.description()
    return _frag


def fragment_plan_fragment():
    _frag = sgqlc.operation.Fragment(_schema.Plan, 'PlanFragment')
    _frag.id()
    _frag.ref_id()
    _frag.display_name()
    _frag.description()
    _frag.billing_id()
    _frag.version_number()
    _frag.additional_meta_data()
    _frag.hidden_from_widgets()
    _frag_product = _frag.product()
    _frag_product.__fragment__(fragment_product_fragment())
    _frag_base_plan = _frag.base_plan()
    _frag_base_plan.ref_id()
    _frag_base_plan.display_name()
    _frag_entitlements = _frag.entitlements()
    _frag_entitlements.__fragment__(fragment_package_entitlement_fragment())
    _frag_inherited_entitlements = _frag.inherited_entitlements()
    _frag_inherited_entitlements.__fragment__(fragment_package_entitlement_fragment())
    _frag_compatible_addons = _frag.compatible_addons()
    _frag_compatible_addons.__fragment__(fragment_addon_fragment())
    _frag_compatible_package_groups = _frag.compatible_package_groups()
    _frag_compatible_package_groups.__fragment__(fragment_plan_compatible_package_groups_fragment())
    _frag_prices = _frag.prices()
    _frag_prices.__fragment__(fragment_price_fragment())
    _frag_overage_prices = _frag.overage_prices()
    _frag_overage_prices.__fragment__(fragment_overage_price_fragment())
    _frag.pricing_type()
    _frag_default_trial_config = _frag.default_trial_config()
    _frag_default_trial_config.duration()
    _frag_default_trial_config.units()
    _frag_default_trial_config_budget = _frag_default_trial_config.budget()
    _frag_default_trial_config_budget.limit()
    _frag_default_trial_config.trial_end_behavior()
    return _frag


def fragment_plan_compatible_package_groups_fragment():
    _frag = sgqlc.operation.Fragment(_schema.PlanCompatiblePackageGroups, 'PlanCompatiblePackageGroupsFragment')
    _frag.package_group_id()
    _frag.display_name()
    _frag_addons = _frag.addons()
    _frag_addons.__fragment__(fragment_addon_fragment())
    _frag_options = _frag.options()
    _frag_options.min_items()
    _frag_options.free_items()
    return _frag


def fragment_customer_resource_fragment():
    _frag = sgqlc.operation.Fragment(_schema.CustomerResource, 'CustomerResourceFragment')
    _frag.resource_id()
    return _frag


def fragment_page_info_fragment():
    _frag = sgqlc.operation.Fragment(_schema.PageInfo, 'PageInfoFragment')
    _frag.start_cursor()
    _frag.end_cursor()
    _frag.has_next_page()
    _frag.has_previous_page()
    return _frag


def fragment_subscription_query_fragment():
    _frag = sgqlc.operation.Fragment(_schema.SubscriptionQuery, 'SubscriptionQueryFragment')
    _frag.subscription_id()
    _frag.status()
    _frag.pricing_type()
    _frag.start_date()
    _frag.current_billing_period_end()
    _frag_customer = _frag.customer()
    _frag_customer.customer_id()
    _frag_paying_customer = _frag.paying_customer()
    _frag_paying_customer.customer_id()
    _frag_resource = _frag.resource()
    _frag_resource.resource_id()
    _frag_plan = _frag.plan()
    _frag_plan.ref_id(__alias__='plan_id')
    _frag_plan.display_name()
    _frag_addons = _frag.addons()
    _frag_addons.quantity()
    _frag_addons_addon = _frag_addons.addon()
    _frag_addons_addon.ref_id(__alias__='addon_id')
    _frag_trial_configuration = _frag.trial_configuration()
    _frag_trial_configuration.trial_end_behavior()
    _frag.trial_end_date()
    return _frag


def fragment_slim_subscription_fragment_v2():
    _frag = sgqlc.operation.Fragment(_schema.CustomerSubscription, 'SlimSubscriptionFragmentV2')
    _frag.subscription_id()
    _frag.status()
    _frag.pricing_type()
    _frag.start_date()
    _frag.cancellation_date()
    _frag.current_billing_period_end()
    _frag_customer = _frag.customer()
    _frag_customer.customer_id()
    _frag_paying_customer = _frag.paying_customer()
    _frag_paying_customer.customer_id()
    _frag_resource = _frag.resource()
    _frag_resource.resource_id()
    _frag_plan = _frag.plan()
    _frag_plan.ref_id(__alias__='plan_id')
    _frag_plan.display_name()
    _frag_addons = _frag.addons()
    _frag_addons.quantity()
    _frag_addons_addon = _frag_addons.addon()
    _frag_addons_addon.ref_id(__alias__='addon_id')
    _frag_trial_configuration = _frag.trial_configuration()
    _frag_trial_configuration.trial_end_behavior()
    _frag.trial_end_date()
    return _frag


def fragment_slim_subscription_fragment():
    _frag = sgqlc.operation.Fragment(_schema.CustomerSubscription, 'SlimSubscriptionFragment')
    _frag.id()
    _frag.subscription_id()
    _frag.ref_id()
    _frag.status()
    _frag.additional_meta_data()
    _frag.billing_id()
    _frag.billing_link_url()
    _frag.effective_end_date()
    _frag.cancellation_date()
    _frag.current_billing_period_end()
    _frag.pricing_type()
    _frag_latest_invoice = _frag.latest_invoice()
    _frag_latest_invoice.__fragment__(fragment_subscription_invoice_fragment())
    _frag.payment_collection()
    _frag.billing_sync_error()
    _frag_resource = _frag.resource()
    _frag_resource.__fragment__(fragment_customer_resource_fragment())
    _frag_experiment_info = _frag.experiment_info()
    _frag_experiment_info.name()
    _frag_experiment_info.id()
    _frag_experiment_info.group_type()
    _frag_experiment_info.group_name()
    _frag_prices = _frag.prices()
    _frag_prices.usage_limit()
    _frag_prices_price = _frag_prices.price()
    _frag_prices_price.__fragment__(fragment_price_fragment())
    _frag_total_price = _frag.total_price()
    _frag_total_price.__fragment__(fragment_total_price_fragment())
    _frag_plan = _frag.plan()
    _frag_plan.id()
    _frag_plan.ref_id()
    _frag_addons = _frag.addons()
    _frag_addons.quantity()
    _frag_addons_addon = _frag_addons.addon()
    _frag_addons_addon.id()
    _frag_addons_addon.ref_id()
    _frag_customer = _frag.customer()
    _frag_customer.id()
    _frag_customer.ref_id()
    return _frag


def fragment_subscription_scheduled_update_data():
    _frag = sgqlc.operation.Fragment(_schema.SubscriptionScheduledUpdate, 'SubscriptionScheduledUpdateData')
    _frag.subscription_schedule_type()
    _frag.schedule_status()
    _frag.scheduled_execution_time()
    _frag_target_package = _frag.target_package()
    _frag_target_package.id()
    _frag_target_package.ref_id()
    _frag_target_package.display_name()
    _frag_schedule_variables = _frag.schedule_variables()
    _frag_schedule_variables.__fragment__(fragment_schedule_variables_fragment())
    return _frag


def fragment_subscription_future_update_data():
    _frag = sgqlc.operation.Fragment(_schema.SubscriptionFutureUpdate, 'SubscriptionFutureUpdateData')
    _frag.subscription_schedule_type()
    _frag.schedule_status()
    _frag.scheduled_execution_time()
    _frag_target_package = _frag.target_package()
    _frag_target_package.id()
    _frag_target_package.ref_id()
    _frag_target_package.display_name()
    _frag_schedule_variables = _frag.schedule_variables()
    _frag_schedule_variables.__fragment__(fragment_schedule_variables_fragment())
    return _frag


def fragment_subscription_invoice_fragment():
    _frag = sgqlc.operation.Fragment(_schema.SubscriptionInvoice, 'SubscriptionInvoiceFragment')
    _frag.billing_id()
    _frag.status()
    _frag.created_at()
    _frag.due_date()
    _frag.updated_at()
    _frag.error_message()
    _frag.requires_action()
    _frag.payment_secret()
    _frag.payment_url()
    _frag.pdf_url()
    _frag.billing_reason()
    _frag.currency()
    _frag.sub_total()
    _frag.sub_total_excluding_tax()
    _frag.total()
    _frag.total_excluding_tax()
    _frag.tax()
    _frag.amount_due()
    _frag.attempt_count()
    return _frag


def fragment_subscription_fragment():
    _frag = sgqlc.operation.Fragment(_schema.CustomerSubscription, 'SubscriptionFragment')
    _frag.id()
    _frag.subscription_id()
    _frag_paying_customer = _frag.paying_customer()
    _frag_paying_customer.__fragment__(fragment_slim_customer_fragment())
    _frag.start_date()
    _frag.end_date()
    _frag.trial_end_date()
    _frag.cancellation_date()
    _frag.effective_end_date()
    _frag.status()
    _frag.ref_id()
    _frag.current_billing_period_end()
    _frag.additional_meta_data()
    _frag.billing_id()
    _frag.billing_link_url()
    _frag_latest_invoice = _frag.latest_invoice()
    _frag_latest_invoice.__fragment__(fragment_subscription_invoice_fragment())
    _frag.payment_collection()
    _frag.payment_collection_method()
    _frag.billing_sync_error()
    _frag_resource = _frag.resource()
    _frag_resource.__fragment__(fragment_customer_resource_fragment())
    _frag_experiment_info = _frag.experiment_info()
    _frag_experiment_info.name()
    _frag_experiment_info.group_type()
    _frag_experiment_info.group_name()
    _frag_experiment_info.id()
    _frag_prices = _frag.prices()
    _frag_prices.usage_limit()
    _frag_prices_price = _frag_prices.price()
    _frag_prices_price.__fragment__(fragment_price_fragment())
    _frag_total_price = _frag.total_price()
    _frag_total_price.__fragment__(fragment_total_price_fragment())
    _frag.pricing_type()
    _frag_plan = _frag.plan()
    _frag_plan.__fragment__(fragment_plan_fragment())
    _frag_addons = _frag.addons()
    _frag_addons.id()
    _frag_addons.quantity()
    _frag_addons_addon = _frag_addons.addon()
    _frag_addons_addon.__fragment__(fragment_addon_fragment())
    _frag_scheduled_updates = _frag.scheduled_updates()
    _frag_scheduled_updates.__fragment__(fragment_subscription_scheduled_update_data())
    _frag_future_updates = _frag.future_updates()
    _frag_future_updates.__fragment__(fragment_subscription_future_update_data())
    _frag_trial_configuration = _frag.trial_configuration()
    _frag_trial_configuration.__fragment__(fragment_subscription_trial_configuration_fragment())
    return _frag


def fragment_subscription_trial_configuration_fragment():
    _frag = sgqlc.operation.Fragment(_schema.TrialConfiguration, 'SubscriptionTrialConfigurationFragment')
    _frag.trial_end_behavior()
    return _frag


def fragment_promotional_entitlement_fragment():
    _frag = sgqlc.operation.Fragment(_schema.PromotionalEntitlement, 'PromotionalEntitlementFragment')
    _frag.status()
    _frag.usage_limit()
    _frag.feature_id()
    _frag.has_unlimited_usage()
    _frag.has_soft_limit()
    _frag.reset_period()
    _frag.end_date()
    _frag.is_visible()
    _frag_feature = _frag.feature()
    _frag_feature.feature_type()
    _frag_feature.meter_type()
    _frag_feature.feature_units()
    _frag_feature.feature_units_plural()
    _frag_feature.display_name()
    _frag_feature.description()
    _frag_feature.ref_id()
    _frag_feature.additional_meta_data()
    return _frag


def fragment_slim_customer_fragment():
    _frag = sgqlc.operation.Fragment(_schema.Customer, 'SlimCustomerFragment')
    _frag.id()
    _frag.name()
    _frag.email()
    _frag.created_at()
    _frag.updated_at()
    _frag.ref_id()
    _frag.customer_id()
    _frag.billing_id()
    _frag.additional_meta_data()
    _frag.aws_marketplace_customer_id()
    return _frag


def fragment_customer_fragment():
    _frag = sgqlc.operation.Fragment(_schema.Customer, 'CustomerFragment')
    _frag.__fragment__(fragment_slim_customer_fragment())
    _frag.has_payment_method()
    _frag.has_active_subscription()
    _frag.default_payment_expiration_month()
    _frag.default_payment_expiration_year()
    _frag.default_payment_method_last4_digits()
    _frag.default_payment_method_type()
    _frag_trialed_plans = _frag.trialed_plans()
    _frag_trialed_plans.product_id()
    _frag_trialed_plans.product_ref_id()
    _frag_trialed_plans.plan_ref_id()
    _frag_trialed_plans.plan_id()
    _frag_experiment_info = _frag.experiment_info()
    _frag_experiment_info.group_type()
    _frag_experiment_info.group_name()
    _frag_experiment_info.id()
    _frag_experiment_info.name()
    _frag_coupon = _frag.coupon()
    _frag_coupon.__fragment__(fragment_coupon_fragment())
    _frag_eligible_for_trial = _frag.eligible_for_trial()
    _frag_eligible_for_trial.product_id()
    _frag_eligible_for_trial.product_ref_id()
    _frag_eligible_for_trial.eligible()
    _frag_promotional_entitlements = _frag.promotional_entitlements()
    _frag_promotional_entitlements.__fragment__(fragment_promotional_entitlement_fragment())
    return _frag


def fragment_customer_with_subscriptions_fragment():
    _frag = sgqlc.operation.Fragment(_schema.Customer, 'CustomerWithSubscriptionsFragment')
    _frag.__fragment__(fragment_customer_fragment())
    _frag_subscriptions = _frag.subscriptions()
    _frag_subscriptions.__fragment__(fragment_subscription_fragment())
    return _frag


def fragment_customer_statistics_fragment():
    _frag = sgqlc.operation.Fragment(_schema.Customer, 'CustomerStatisticsFragment')
    _frag_statistics = _frag.statistics()
    _frag_statistics_active_subscriptions_by_pricing_type = _frag_statistics.active_subscriptions_by_pricing_type()
    _frag_statistics_active_subscriptions_by_pricing_type.pricing_type()
    _frag_statistics_active_subscriptions_by_pricing_type.total_count()
    return _frag


def fragment_subscription_preview_fragment():
    _frag = sgqlc.operation.Fragment(_schema.SubscriptionPreview, 'SubscriptionPreviewFragment')
    _frag_sub_total = _frag.sub_total()
    _frag_sub_total.amount()
    _frag_sub_total.currency()
    _frag_total_excluding_tax = _frag.total_excluding_tax()
    _frag_total_excluding_tax.amount()
    _frag_total_excluding_tax.currency()
    _frag_total = _frag.total()
    _frag_total.amount()
    _frag_total.currency()
    _frag_discount_amount = _frag.discount_amount()
    _frag_discount_amount.amount()
    _frag_discount_amount.currency()
    _frag_tax_details = _frag.tax_details()
    _frag_tax_details.display_name()
    _frag_tax_details.percentage()
    _frag_tax_details.inclusive()
    _frag_tax = _frag.tax()
    _frag_tax.amount()
    _frag_tax.currency()
    _frag_billing_period_range = _frag.billing_period_range()
    _frag_billing_period_range.start()
    _frag_billing_period_range.end()
    _frag_discount = _frag.discount()
    _frag_discount.name()
    _frag_discount.type()
    _frag_discount.value()
    _frag_discount.duration_type()
    _frag_discount.duration_in_months()
    _frag_subscription = _frag.subscription()
    _frag_subscription_sub_total = _frag_subscription.sub_total()
    _frag_subscription_sub_total.amount()
    _frag_subscription_sub_total.currency()
    _frag_subscription_total_excluding_tax = _frag_subscription.total_excluding_tax()
    _frag_subscription_total_excluding_tax.amount()
    _frag_subscription_total_excluding_tax.currency()
    _frag_subscription_total = _frag_subscription.total()
    _frag_subscription_total.amount()
    _frag_subscription_total.currency()
    _frag_subscription_tax = _frag_subscription.tax()
    _frag_subscription_tax.amount()
    _frag_subscription_tax.currency()
    _frag_subscription_discount_amount = _frag_subscription.discount_amount()
    _frag_subscription_discount_amount.amount()
    _frag_subscription_discount_amount.currency()
    _frag_subscription_tax_details = _frag_subscription.tax_details()
    _frag_subscription_tax_details.display_name()
    _frag_subscription_tax_details.percentage()
    _frag_subscription_tax_details.inclusive()
    _frag_subscription_discount = _frag_subscription.discount()
    _frag_subscription_discount.name()
    _frag_subscription_discount.type()
    _frag_subscription_discount.value()
    _frag_subscription_discount.duration_type()
    _frag_subscription_discount.duration_in_months()
    _frag_proration = _frag.proration()
    _frag_proration.proration_date()
    _frag_proration_credit = _frag_proration.credit()
    _frag_proration_credit.amount()
    _frag_proration_credit.currency()
    _frag_proration_debit = _frag_proration.debit()
    _frag_proration_debit.amount()
    _frag_proration_debit.currency()
    _frag_proration_net_amount = _frag_proration.net_amount()
    _frag_proration_net_amount.amount()
    _frag_proration_net_amount.currency()
    _frag.is_plan_downgrade()
    _frag.has_scheduled_updates()
    _frag_credits = _frag.credits()
    _frag_credits_initial = _frag_credits.initial()
    _frag_credits_initial.amount()
    _frag_credits_initial.currency()
    _frag_credits_used = _frag_credits.used()
    _frag_credits_used.amount()
    _frag_credits_used.currency()
    _frag_credits_remaining = _frag_credits.remaining()
    _frag_credits_remaining.amount()
    _frag_credits_remaining.currency()
    return _frag


def fragment_subscription_preview_invoice_fragment():
    _frag = sgqlc.operation.Fragment(_schema.SubscriptionPreviewInvoice, 'SubscriptionPreviewInvoiceFragment')
    _frag_total = _frag.total()
    _frag_total.amount()
    _frag_total.currency()
    _frag_sub_total = _frag.sub_total()
    _frag_sub_total.amount()
    _frag_sub_total.currency()
    _frag_total_excluding_tax = _frag.total_excluding_tax()
    _frag_total_excluding_tax.amount()
    _frag_total_excluding_tax.currency()
    _frag_tax = _frag.tax()
    _frag_tax.amount()
    _frag_tax.currency()
    _frag_discount = _frag.discount()
    _frag_discount.amount()
    _frag_discount.currency()
    _frag_tax_details = _frag.tax_details()
    _frag_tax_details.display_name()
    _frag_tax_details.percentage()
    _frag_tax_details.inclusive()
    _frag_discount_details = _frag.discount_details()
    _frag_discount_details.type()
    _frag_discount_details.value()
    _frag_discount_details.duration_type()
    _frag_discount_details.duration_in_months()
    return _frag


def fragment_immediate_subscription_preview_invoice_fragment():
    _frag = sgqlc.operation.Fragment(_schema.ImmediateSubscriptionPreviewInvoice, 'ImmediateSubscriptionPreviewInvoiceFragment')
    _frag_total = _frag.total()
    _frag_total.amount()
    _frag_total.currency()
    _frag_sub_total = _frag.sub_total()
    _frag_sub_total.amount()
    _frag_sub_total.currency()
    _frag_total_excluding_tax = _frag.total_excluding_tax()
    _frag_total_excluding_tax.amount()
    _frag_total_excluding_tax.currency()
    _frag_tax = _frag.tax()
    _frag_tax.amount()
    _frag_tax.currency()
    _frag_discount = _frag.discount()
    _frag_discount.amount()
    _frag_discount.currency()
    _frag_tax_details = _frag.tax_details()
    _frag_tax_details.display_name()
    _frag_tax_details.percentage()
    _frag_tax_details.inclusive()
    _frag_discount_details = _frag.discount_details()
    _frag_discount_details.type()
    _frag_discount_details.value()
    _frag_discount_details.duration_type()
    _frag_discount_details.duration_in_months()
    _frag_credits = _frag.credits()
    _frag_credits_initial = _frag_credits.initial()
    _frag_credits_initial.amount()
    _frag_credits_initial.currency()
    _frag_credits_used = _frag_credits.used()
    _frag_credits_used.amount()
    _frag_credits_used.currency()
    _frag_credits_remaining = _frag_credits.remaining()
    _frag_credits_remaining.amount()
    _frag_credits_remaining.currency()
    _frag_proration = _frag.proration()
    _frag_proration.proration_date()
    _frag_proration.has_prorations()
    _frag_proration_credit = _frag_proration.credit()
    _frag_proration_credit.amount()
    _frag_proration_credit.currency()
    _frag_proration_debit = _frag_proration.debit()
    _frag_proration_debit.amount()
    _frag_proration_debit.currency()
    _frag_proration_net_amount = _frag_proration.net_amount()
    _frag_proration_net_amount.amount()
    _frag_proration_net_amount.currency()
    return _frag


def fragment_subscription_preview_v2_fragment():
    _frag = sgqlc.operation.Fragment(_schema.SubscriptionPreviewV2, 'SubscriptionPreviewV2Fragment')
    _frag_immediate_invoice = _frag.immediate_invoice()
    _frag_immediate_invoice.__fragment__(fragment_immediate_subscription_preview_invoice_fragment())
    _frag_recurring_invoice = _frag.recurring_invoice()
    _frag_recurring_invoice.__fragment__(fragment_subscription_preview_invoice_fragment())
    _frag_billing_period_range = _frag.billing_period_range()
    _frag_billing_period_range.start()
    _frag_billing_period_range.end()
    _frag.is_plan_downgrade()
    _frag.has_scheduled_updates()
    return _frag


def fragment_subscription_invoice_preview_fragment():
    _frag = sgqlc.operation.Fragment(_schema.SubscriptionInvoicePreview, 'SubscriptionInvoicePreviewFragment')
    _frag_amount_due = _frag.amount_due()
    _frag_amount_due.amount()
    _frag_amount_due.currency()
    _frag_minimum_spend_adjustment = _frag.minimum_spend_adjustment()
    _frag_minimum_spend_adjustment.amount()
    _frag_minimum_spend_adjustment.currency()
    _frag_total = _frag.total()
    _frag_total.amount()
    _frag_total.currency()
    _frag_total_excluding_tax = _frag.total_excluding_tax()
    _frag_total_excluding_tax.amount()
    _frag_total_excluding_tax.currency()
    _frag_sub_total = _frag.sub_total()
    _frag_sub_total.amount()
    _frag_sub_total.currency()
    _frag_sub_total_excluding_tax = _frag.sub_total_excluding_tax()
    _frag_sub_total_excluding_tax.amount()
    _frag_sub_total_excluding_tax.currency()
    _frag_tax = _frag.tax()
    _frag_tax.amount()
    _frag_tax.currency()
    _frag_tax_details = _frag.tax_details()
    _frag_tax_details.display_name()
    _frag_tax_details.percentage()
    _frag_tax_details.inclusive()
    _frag_discount = _frag.discount()
    _frag_discount.amount()
    _frag_discount.currency()
    _frag_discount_details = _frag.discount_details()
    _frag_discount_details.name()
    _frag_discount_details.type()
    _frag_discount_details.value()
    _frag_discount_details.duration_type()
    _frag_discount_details.duration_in_months()
    _frag_credits = _frag.credits()
    _frag_credits_initial = _frag_credits.initial()
    _frag_credits_initial.amount()
    _frag_credits_initial.currency()
    _frag_credits_used = _frag_credits.used()
    _frag_credits_used.amount()
    _frag_credits_used.currency()
    _frag_credits_remaining = _frag_credits.remaining()
    _frag_credits_remaining.amount()
    _frag_credits_remaining.currency()
    _frag.last_updated_at()
    _frag_lines = _frag.lines()
    _frag_lines.type()
    _frag_lines.description()
    _frag_lines.cost_description()
    _frag_lines_amount = _frag_lines.amount()
    _frag_lines_amount.amount()
    _frag_lines_amount.currency()
    _frag_lines_unit_price = _frag_lines.unit_price()
    _frag_lines_unit_price.amount()
    _frag_lines_unit_price.currency()
    _frag_lines.quantity()
    _frag_lines.proration()
    _frag_lines_price = _frag_lines.price()
    _frag_lines_price.__fragment__(fragment_price_fragment())
    _frag_lines.usage_limit()
    _frag_lines_period = _frag_lines.period()
    _frag_lines_period.start()
    _frag_lines_period.end()
    _frag_lines.has_soft_limit()
    _frag_lines_lines = _frag_lines.lines()
    _frag_lines_lines.type()
    _frag_lines_lines.description()
    _frag_lines_lines.cost_description()
    _frag_lines_lines.quantity()
    _frag_lines_lines.proration()
    _frag_lines_lines.usage_limit()
    _frag_lines_lines.has_soft_limit()
    return _frag


def fragment_feature_fragment():
    _frag = sgqlc.operation.Fragment(_schema.EntitlementFeature, 'FeatureFragment')
    _frag.__typename__()
    _frag.feature_type()
    _frag.meter_type()
    _frag.feature_units()
    _frag.feature_units_plural()
    _frag.description()
    _frag.display_name()
    _frag.ref_id()
    _frag_unit_transformation = _frag.unit_transformation()
    _frag_unit_transformation.divide()
    _frag_unit_transformation.round()
    return _frag


def fragment_reset_period_configuration_fragment():
    _frag = sgqlc.operation.Fragment(_schema.ResetPeriodConfiguration, 'ResetPeriodConfigurationFragment')
    _frag.__typename__()
    _frag__as__YearlyResetPeriodConfig = _frag.__as__(_schema.YearlyResetPeriodConfig)
    _frag__as__YearlyResetPeriodConfig.yearly_according_to()
    _frag__as__MonthlyResetPeriodConfig = _frag.__as__(_schema.MonthlyResetPeriodConfig)
    _frag__as__MonthlyResetPeriodConfig.monthly_according_to()
    _frag__as__WeeklyResetPeriodConfig = _frag.__as__(_schema.WeeklyResetPeriodConfig)
    _frag__as__WeeklyResetPeriodConfig.weekly_according_to()
    return _frag


def fragment_usage_updated_fragment():
    _frag = sgqlc.operation.Fragment(_schema.UsageMeasurementUpdated, 'UsageUpdatedFragment')
    _frag.customer_id()
    _frag.resource_id()
    _frag.feature_id()
    _frag.current_usage()
    _frag.usage_period_start()
    _frag.usage_period_end()
    _frag.next_reset_date()
    return _frag


def fragment_entitlement_fragment():
    _frag = sgqlc.operation.Fragment(_schema.Entitlement, 'EntitlementFragment')
    _frag.__typename__()
    _frag.is_granted()
    _frag.access_denied_reason()
    _frag.customer_id()
    _frag.resource_id()
    _frag.usage_limit()
    _frag.has_unlimited_usage()
    _frag.has_soft_limit()
    _frag.current_usage()
    _frag.requested_usage()
    _frag.requested_values()
    _frag.enum_values()
    _frag.entitlement_updated_at()
    _frag.usage_updated_at()
    _frag.usage_period_anchor()
    _frag.usage_period_start()
    _frag.usage_period_end()
    _frag.next_reset_date()
    _frag.reset_period()
    _frag_reset_period_configuration = _frag.reset_period_configuration()
    _frag_reset_period_configuration.__fragment__(fragment_reset_period_configuration_fragment())
    _frag_feature = _frag.feature()
    _frag_feature.__fragment__(fragment_feature_fragment())
    return _frag


def fragment_typography_configuration_fragment():
    _frag = sgqlc.operation.Fragment(_schema.TypographyConfiguration, 'TypographyConfigurationFragment')
    _frag.font_family()
    _frag_h1 = _frag.h1()
    _frag_h1.__fragment__(fragment_font_variant_fragment())
    _frag_h2 = _frag.h2()
    _frag_h2.__fragment__(fragment_font_variant_fragment())
    _frag_h3 = _frag.h3()
    _frag_h3.__fragment__(fragment_font_variant_fragment())
    _frag_body = _frag.body()
    _frag_body.__fragment__(fragment_font_variant_fragment())
    return _frag


def fragment_font_variant_fragment():
    _frag = sgqlc.operation.Fragment(_schema.FontVariant, 'FontVariantFragment')
    _frag.font_size()
    _frag.font_weight()
    return _frag


def fragment_layout_configuration_fragment():
    _frag = sgqlc.operation.Fragment(_schema.PaywallLayoutConfiguration, 'LayoutConfigurationFragment')
    _frag.alignment()
    _frag.plan_width()
    _frag.plan_margin()
    _frag.plan_padding()
    return _frag


def fragment_paywall_configuration_fragment():
    _frag = sgqlc.operation.Fragment(_schema.PaywallConfiguration, 'PaywallConfigurationFragment')
    _frag_palette = _frag.palette()
    _frag_palette.primary()
    _frag_palette.text_color()
    _frag_palette.background_color()
    _frag_palette.border_color()
    _frag_palette.current_plan_background()
    _frag_typography = _frag.typography()
    _frag_typography.__fragment__(fragment_typography_configuration_fragment())
    _frag_layout = _frag.layout()
    _frag_layout.__fragment__(fragment_layout_configuration_fragment())
    _frag.custom_css()
    return _frag


def fragment_paywall_currency_fragment():
    _frag = sgqlc.operation.Fragment(_schema.PaywallCurrency, 'PaywallCurrencyFragment')
    _frag.code()
    _frag.symbol()
    return _frag


def fragment_product_fragment():
    _frag = sgqlc.operation.Fragment(_schema.Product, 'ProductFragment')
    _frag.ref_id()
    _frag.display_name()
    _frag.description()
    _frag.additional_meta_data()
    _frag_product_settings = _frag.product_settings()
    _frag_product_settings_downgrade_plan = _frag_product_settings.downgrade_plan()
    _frag_product_settings_downgrade_plan.ref_id()
    _frag_product_settings_downgrade_plan.display_name()
    return _frag


def fragment_entitlements_updated_payload():
    _frag = sgqlc.operation.Fragment(_schema.EntitlementsUpdated, 'EntitlementsUpdatedPayload')
    _frag.customer_id()
    _frag.resource_id()
    _frag_entitlements = _frag.entitlements()
    _frag_entitlements.__fragment__(fragment_entitlement_fragment())
    return _frag


def fragment_entitlement_usage_updated():
    _frag = sgqlc.operation.Fragment(_schema.UsageUpdated, 'EntitlementUsageUpdated')
    _frag_usage = _frag.usage()
    _frag_usage.__fragment__(fragment_usage_updated_fragment())
    _frag_entitlement = _frag.entitlement()
    _frag_entitlement.__fragment__(fragment_entitlement_fragment())
    return _frag


def fragment_package_published_payload():
    _frag = sgqlc.operation.Fragment(_schema.PackagePublished, 'PackagePublishedPayload')
    _frag.account_id()
    _frag.environment_id()
    _frag.package_type()
    _frag.package_ref_id()
    _frag.package_version()
    _frag.migration_type()
    return _frag


def fragment_customer_portal_fragment():
    _frag = sgqlc.operation.Fragment(_schema.CustomerPortal, 'CustomerPortalFragment')
    _frag_subscriptions = _frag.subscriptions()
    _frag_subscriptions.__fragment__(fragment_customer_portal_subscription_fragment())
    _frag_entitlements = _frag.entitlements()
    _frag_entitlements.__fragment__(fragment_customer_portal_entitlement_fragment())
    _frag_promotional_entitlements = _frag.promotional_entitlements()
    _frag_promotional_entitlements.__fragment__(fragment_customer_portal_promotional_entitlement_fragment())
    _frag_billing_information = _frag.billing_information()
    _frag_billing_information.__fragment__(fragment_customer_portal_billing_information_fragment())
    _frag.show_watermark()
    _frag.billing_portal_url()
    _frag.can_upgrade_subscription()
    _frag_configuration = _frag.configuration()
    _frag_configuration.__fragment__(fragment_customer_portal_configuration_fragment())
    _frag_resource = _frag.resource()
    _frag_resource.__fragment__(fragment_customer_resource_fragment())
    return _frag


def fragment_checkout_state_fragment():
    _frag = sgqlc.operation.Fragment(_schema.CheckoutState, 'CheckoutStateFragment')
    _frag_configuration = _frag.configuration()
    _frag_configuration.__fragment__(fragment_checkout_configuration_fragment())
    _frag.setup_secret()
    _frag_customer = _frag.customer()
    _frag_customer.__fragment__(fragment_customer_fragment())
    _frag_active_subscription = _frag.active_subscription()
    _frag_active_subscription.__fragment__(fragment_subscription_fragment())
    _frag_resource = _frag.resource()
    _frag_resource.__fragment__(fragment_customer_resource_fragment())
    _frag_plan = _frag.plan()
    _frag_plan.__fragment__(fragment_plan_fragment())
    _frag_billing_integration = _frag.billing_integration()
    _frag_billing_integration.billing_identifier()
    _frag_billing_integration_credentials = _frag_billing_integration.credentials()
    _frag_billing_integration_credentials.account_id()
    _frag_billing_integration_credentials.public_key()
    return _frag


def fragment_checkout_configuration_fragment():
    _frag = sgqlc.operation.Fragment(_schema.CheckoutConfiguration, 'CheckoutConfigurationFragment')
    _frag_palette = _frag.palette()
    _frag_palette.primary()
    _frag_palette.text_color()
    _frag_palette.background_color()
    _frag_palette.border_color()
    _frag_palette.summary_background_color()
    _frag_palette.__typename__()
    _frag_typography = _frag.typography()
    _frag_typography.__fragment__(fragment_typography_configuration_fragment())
    _frag_typography.__typename__()
    _frag.custom_css()
    _frag_content = _frag.content()
    _frag_content.collect_phone_number()
    _frag.__typename__()
    return _frag


def fragment_customer_portal_configuration_fragment():
    _frag = sgqlc.operation.Fragment(_schema.CustomerPortalConfiguration, 'CustomerPortalConfigurationFragment')
    _frag_palette = _frag.palette()
    _frag_palette.primary()
    _frag_palette.text_color()
    _frag_palette.background_color()
    _frag_palette.border_color()
    _frag_palette.current_plan_background()
    _frag_palette.icons_color()
    _frag_palette.paywall_background_color()
    _frag_typography = _frag.typography()
    _frag_typography.__fragment__(fragment_typography_configuration_fragment())
    _frag.custom_css()
    return _frag


def fragment_customer_portal_subscription_price_fragment():
    _frag = sgqlc.operation.Fragment(_schema.CustomerPortalSubscriptionPrice, 'CustomerPortalSubscriptionPriceFragment')
    _frag.billing_period()
    _frag.billing_model()
    _frag.block_size()
    _frag_price = _frag.price()
    _frag_price.amount()
    _frag_price.currency()
    _frag_credit_rate = _frag.credit_rate()
    _frag_credit_rate.amount()
    _frag_credit_rate.custom_currency_id()
    _frag_feature = _frag.feature()
    _frag_feature.id()
    _frag_feature.ref_id()
    _frag_feature.display_name()
    _frag_feature.feature_units()
    _frag_feature.feature_units_plural()
    return _frag


def fragment_customer_portal_subscription_fragment():
    _frag = sgqlc.operation.Fragment(_schema.CustomerPortalSubscription, 'CustomerPortalSubscriptionFragment')
    _frag.subscription_id()
    _frag.plan_id()
    _frag.plan_name()
    _frag.pricing_type()
    _frag_prices = _frag.prices()
    _frag_prices.__fragment__(fragment_customer_portal_subscription_price_fragment())
    _frag_pricing = _frag.pricing()
    _frag_pricing.unit_quantity()
    _frag_pricing.billing_period()
    _frag_pricing.billing_model()
    _frag_pricing.pricing_type()
    _frag_pricing.usage_based_estimated_bill()
    _frag_pricing_price = _frag_pricing.price()
    _frag_pricing_price.amount()
    _frag_pricing_price.currency()
    _frag_pricing_credit_rate = _frag_pricing.credit_rate()
    _frag_pricing_credit_rate.amount()
    _frag_pricing_credit_rate.custom_currency_id()
    _frag_pricing_feature = _frag_pricing.feature()
    _frag_pricing_feature.feature_units()
    _frag_pricing_feature.feature_units_plural()
    _frag_pricing_feature.display_name()
    _frag.status()
    _frag.trial_remaining_days()
    _frag_billing_period_range = _frag.billing_period_range()
    _frag_billing_period_range.start()
    _frag_billing_period_range.end()
    _frag_total_price = _frag.total_price()
    _frag_total_price_sub_total = _frag_total_price.sub_total()
    _frag_total_price_sub_total.amount()
    _frag_total_price_sub_total.currency()
    _frag_total_price_total = _frag_total_price.total()
    _frag_total_price_total.amount()
    _frag_total_price_total.currency()
    _frag_total_price_addons_total = _frag_total_price.addons_total()
    _frag_total_price_addons_total.amount()
    _frag_total_price_addons_total.currency()
    _frag_addons = _frag.addons()
    _frag_addons.__fragment__(fragment_customer_portal_subscription_addon_fragment())
    _frag_scheduled_updates = _frag.scheduled_updates()
    _frag_scheduled_updates.__fragment__(fragment_customer_portal_subscription_scheduled_update_data_fragment())
    return _frag


def fragment_customer_portal_subscription_addon_fragment():
    _frag = sgqlc.operation.Fragment(_schema.CustomerPortalAddon, 'CustomerPortalSubscriptionAddonFragment')
    _frag.addon_id()
    _frag.description()
    _frag.display_name()
    _frag.quantity()
    return _frag


def fragment_customer_portal_subscription_scheduled_update_data_fragment():
    _frag = sgqlc.operation.Fragment(_schema.SubscriptionScheduledUpdate, 'CustomerPortalSubscriptionScheduledUpdateDataFragment')
    _frag.subscription_schedule_type()
    _frag.schedule_status()
    _frag.scheduled_execution_time()
    _frag_target_package = _frag.target_package()
    _frag_target_package.id()
    _frag_target_package.ref_id()
    _frag_target_package.display_name()
    _frag_target_package.pricing_type()
    _frag_schedule_variables = _frag.schedule_variables()
    _frag_schedule_variables.__fragment__(fragment_schedule_variables_fragment())
    return _frag


def fragment_customer_portal_entitlement_fragment():
    _frag = sgqlc.operation.Fragment(_schema.Entitlement, 'CustomerPortalEntitlementFragment')
    _frag.is_granted()
    _frag.usage_limit()
    _frag.current_usage()
    _frag.has_unlimited_usage()
    _frag.has_soft_limit()
    _frag.usage_period_start()
    _frag.usage_period_end()
    _frag.next_reset_date()
    _frag.reset_period()
    _frag_reset_period_configuration = _frag.reset_period_configuration()
    _frag_reset_period_configuration.__fragment__(fragment_reset_period_configuration_fragment())
    _frag_feature = _frag.feature()
    _frag_feature.__fragment__(fragment_feature_fragment())
    return _frag


def fragment_customer_portal_promotional_entitlement_fragment():
    _frag = sgqlc.operation.Fragment(_schema.CustomerPortalPromotionalEntitlement, 'CustomerPortalPromotionalEntitlementFragment')
    _frag.display_name()
    _frag.has_unlimited_usage()
    _frag.has_soft_limit()
    _frag.usage_limit()
    _frag.period()
    _frag.start_date()
    _frag.end_date()
    return _frag


def fragment_customer_portal_billing_information_fragment():
    _frag = sgqlc.operation.Fragment(_schema.CustomerPortalBillingInformation, 'CustomerPortalBillingInformationFragment')
    _frag.email()
    _frag.name()
    _frag.default_payment_method_last4_digits()
    _frag.default_payment_method_id()
    _frag.default_payment_expiration_month()
    _frag.default_payment_expiration_year()
    _frag.default_payment_method_type()
    return _frag


def fragment_mock_paywall_plan_fragment():
    _frag = sgqlc.operation.Fragment(_schema.PaywallPlan, 'MockPaywallPlanFragment')
    _frag.ref_id()
    _frag.description()
    _frag.display_name()
    _frag.billing_id()
    _frag.additional_meta_data()
    _frag_product = _frag.product()
    _frag_product.ref_id()
    _frag_product.display_name()
    _frag_product.description()
    _frag_product.additional_meta_data()
    _frag_base_plan = _frag.base_plan()
    _frag_base_plan.ref_id()
    _frag_base_plan.display_name()
    _frag_entitlements = _frag.entitlements()
    _frag_entitlements.__fragment__(fragment_mock_paywall_package_entitlement_fragment())
    _frag_inherited_entitlements = _frag.inherited_entitlements()
    _frag_inherited_entitlements.__fragment__(fragment_mock_paywall_package_entitlement_fragment())
    _frag_prices = _frag.prices()
    _frag_prices.__fragment__(fragment_mock_paywall_price_fragment())
    _frag.pricing_type()
    _frag_default_trial_config = _frag.default_trial_config()
    _frag_default_trial_config.duration()
    _frag_default_trial_config.units()
    _frag_default_trial_config_budget = _frag_default_trial_config.budget()
    _frag_default_trial_config_budget.limit()
    _frag_default_trial_config.trial_end_behavior()
    _frag_compatible_addons = _frag.compatible_addons()
    _frag_compatible_addons.__fragment__(fragment_mock_paywall_addon_fragment())
    _frag_compatible_package_groups = _frag.compatible_package_groups()
    _frag_compatible_package_groups.__fragment__(fragment_mock_paywall_plan_compatible_package_groups_fragment())
    return _frag


def fragment_mock_paywall_package_entitlement_fragment():
    _frag = sgqlc.operation.Fragment(_schema.Entitlement, 'MockPaywallPackageEntitlementFragment')
    _frag.usage_limit()
    _frag.has_unlimited_usage()
    _frag.has_soft_limit()
    _frag.reset_period()
    _frag.hidden_from_widgets()
    _frag.display_name_override()
    _frag.enum_values()
    _frag.is_granted()
    _frag_feature = _frag.feature()
    _frag_feature.feature_type()
    _frag_feature.meter_type()
    _frag_feature.feature_units()
    _frag_feature.feature_units_plural()
    _frag_feature.display_name()
    _frag_feature.description()
    _frag_feature.ref_id()
    _frag_feature.additional_meta_data()
    return _frag


def fragment_mock_paywall_price_fragment():
    _frag = sgqlc.operation.Fragment(_schema.PaywallPrice, 'MockPaywallPriceFragment')
    _frag.billing_model()
    _frag.billing_period()
    _frag.billing_id()
    _frag.min_unit_quantity()
    _frag.max_unit_quantity()
    _frag.billing_country_code()
    _frag_price = _frag.price()
    _frag_price.amount()
    _frag_price.currency()
    _frag_credit_rate = _frag.credit_rate()
    _frag_credit_rate.amount()
    _frag_credit_rate.custom_currency_id()
    _frag.tiers_mode()
    _frag_tiers = _frag.tiers()
    _frag_tiers.__fragment__(fragment_price_tier_fragment())
    _frag_feature = _frag.feature()
    _frag_feature.ref_id()
    _frag_feature.feature_units()
    _frag_feature.feature_units_plural()
    _frag_feature.display_name()
    _frag.block_size()
    return _frag


def fragment_paywall_calculated_price_points_fragment():
    _frag = sgqlc.operation.Fragment(_schema.PaywallPricePoint, 'PaywallCalculatedPricePointsFragment')
    _frag.plan_id()
    _frag.additional_charges_may_apply()
    _frag.billing_period()
    _frag.amount()
    _frag.currency()
    _frag.billing_country_code()
    _frag_feature = _frag.feature()
    _frag_feature.ref_id()
    _frag_feature.feature_units()
    _frag_feature.feature_units_plural()
    _frag_feature.display_name()
    _frag_feature.description()
    return _frag


def fragment_mock_paywall_plan_compatible_package_groups_fragment():
    _frag = sgqlc.operation.Fragment(_schema.PaywallPlanCompatiblePackageGroup, 'MockPaywallPlanCompatiblePackageGroupsFragment')
    _frag.package_group_id()
    _frag.display_name()
    _frag.description()
    _frag_addons = _frag.addons()
    _frag_addons.__fragment__(fragment_mock_paywall_addon_fragment())
    _frag_options = _frag.options()
    _frag_options.min_items()
    _frag_options.free_items()
    return _frag


def fragment_mock_paywall_addon_dependency_fragment():
    _frag = sgqlc.operation.Fragment(_schema.PaywallAddon, 'MockPaywallAddonDependencyFragment')
    _frag.ref_id()
    _frag.display_name()
    _frag.description()
    return _frag


def fragment_mock_paywall_addon_fragment():
    _frag = sgqlc.operation.Fragment(_schema.PaywallAddon, 'MockPaywallAddonFragment')
    _frag.ref_id()
    _frag.display_name()
    _frag.description()
    _frag.additional_meta_data()
    _frag.billing_id()
    _frag.max_quantity()
    _frag.hidden_from_widgets()
    _frag_dependencies = _frag.dependencies()
    _frag_dependencies.__fragment__(fragment_mock_paywall_addon_dependency_fragment())
    _frag_entitlements = _frag.entitlements()
    _frag_entitlements.__fragment__(fragment_mock_paywall_package_entitlement_fragment())
    _frag_prices = _frag.prices()
    _frag_prices.__fragment__(fragment_mock_paywall_price_fragment())
    _frag.pricing_type()
    return _frag


def fragment_paywall_fragment():
    _frag = sgqlc.operation.Fragment(_schema.Paywall, 'PaywallFragment')
    _frag_plans = _frag.plans()
    _frag_plans.__fragment__(fragment_plan_fragment())
    _frag_currency = _frag.currency()
    _frag_currency.__fragment__(fragment_paywall_currency_fragment())
    _frag_configuration = _frag.configuration()
    _frag_configuration.__fragment__(fragment_paywall_configuration_fragment())
    _frag_customer = _frag.customer()
    _frag_customer.__fragment__(fragment_customer_fragment())
    _frag_active_subscriptions = _frag.active_subscriptions()
    _frag_active_subscriptions.__fragment__(fragment_subscription_fragment())
    _frag_resource = _frag.resource()
    _frag_resource.__fragment__(fragment_customer_resource_fragment())
    _frag_paywall_calculated_price_points = _frag.paywall_calculated_price_points()
    _frag_paywall_calculated_price_points.__fragment__(fragment_paywall_calculated_price_points_fragment())
    return _frag


def fragment_usage_history_fragment():
    _frag = sgqlc.operation.Fragment(_schema.UsageHistory, 'UsageHistoryFragment')
    _frag.start_date()
    _frag.end_date()
    _frag_markers = _frag.markers()
    _frag_markers.type()
    _frag_markers.timestamp()
    _frag_usage_measurements = _frag.usage_measurements()
    _frag_usage_measurements.date()
    _frag_usage_measurements.value()
    _frag_usage_measurements.is_reset_point()
    _frag_groups = _frag.groups()
    _frag_groups_group_info = _frag_groups.group_info()
    _frag_groups_group_info.key()
    _frag_groups_group_info.value()
    _frag_groups_usage_measurements = _frag_groups.usage_measurements()
    _frag_groups_usage_measurements.date()
    _frag_groups_usage_measurements.value()
    _frag_groups_usage_measurements.is_reset_point()
    return _frag


def fragment_usage_history_v2_fragment():
    _frag = sgqlc.operation.Fragment(_schema.UsageHistoryV2, 'UsageHistoryV2Fragment')
    _frag_markers = _frag.markers()
    _frag_markers.type()
    _frag_markers.timestamp()
    _frag_series = _frag.series()
    _frag_series_tags = _frag_series.tags()
    _frag_series_tags.key()
    _frag_series_tags.value()
    _frag_series_points = _frag_series.points()
    _frag_series_points.timestamp()
    _frag_series_points.value()
    _frag_series_points.is_reset_point()
    return _frag


def fragment_provision_customer_fragment():
    _frag = sgqlc.operation.Fragment(_schema.ProvisionedCustomer, 'ProvisionCustomerFragment')
    _frag_customer = _frag.customer()
    _frag_customer.__fragment__(fragment_slim_customer_fragment())
    _frag.subscription_decision_strategy()
    _frag_subscription = _frag.subscription()
    _frag_subscription.__fragment__(fragment_slim_subscription_fragment())
    _frag_entitlements = _frag.entitlements()
    _frag_entitlements.__fragment__(fragment_entitlement_fragment())
    return _frag


def fragment_apply_subscription_fragment():
    _frag = sgqlc.operation.Fragment(_schema.ApplySubscription, 'ApplySubscriptionFragment')
    _frag_subscription = _frag.subscription()
    _frag_subscription.__fragment__(fragment_subscription_fragment())
    _frag_entitlements = _frag.entitlements()
    _frag_entitlements.__fragment__(fragment_entitlement_fragment())
    return _frag


def fragment_provision_subscription_fragment():
    _frag = sgqlc.operation.Fragment(_schema.ProvisionSubscriptionResult, 'ProvisionSubscriptionFragment')
    _frag.status()
    _frag.checkout_url()
    _frag.checkout_billing_id()
    _frag_subscription = _frag.subscription()
    _frag_subscription.__fragment__(fragment_slim_subscription_fragment())
    _frag_entitlements = _frag.entitlements()
    _frag_entitlements.__fragment__(fragment_entitlement_fragment())
    return _frag


def fragment_report_usage_fragment():
    _frag = sgqlc.operation.Fragment(_schema.UsageMeasurementWithCurrentUsage, 'ReportUsageFragment')
    _frag.id()
    _frag.feature_id()
    _frag.customer_id()
    _frag.resource_id()
    _frag.current_usage()
    _frag.usage_period_start()
    _frag.usage_period_end()
    _frag.next_reset_date()
    _frag.timestamp()
    return _frag


def fragment_schedule_variables_fragment():
    _frag = sgqlc.operation.Fragment(_schema.ScheduleVariables, 'ScheduleVariablesFragment')
    _frag.__typename__()
    _frag__as__PlanChangeVariables = _frag.__as__(_schema.PlanChangeVariables)
    _frag__as__PlanChangeVariables.plan_ref_id()
    _frag__as__PlanChangeVariables.change_type()
    _frag__as__PlanChangeVariables.billing_period()
    _frag__as__PlanChangeVariables_billable_features = _frag__as__PlanChangeVariables.billable_features()
    _frag__as__PlanChangeVariables_billable_features.feature_id()
    _frag__as__PlanChangeVariables_billable_features.quantity()
    _frag__as__PlanChangeVariables_addons = _frag__as__PlanChangeVariables.addons()
    _frag__as__PlanChangeVariables_addons.addon_ref_id()
    _frag__as__PlanChangeVariables_addons.quantity()
    _frag__as__PlanChangeVariables_price_overrides = _frag__as__PlanChangeVariables.price_overrides()
    _frag__as__PlanChangeVariables_price_overrides.plan_ref_id()
    _frag__as__PlanChangeVariables_price_overrides.addon_ref_id()
    _frag__as__PlanChangeVariables_price_overrides.feature_id()
    _frag__as__DowngradeChangeVariables = _frag.__as__(_schema.DowngradeChangeVariables)
    _frag__as__DowngradeChangeVariables.downgrade_plan_ref_id()
    _frag__as__DowngradeChangeVariables.billing_period()
    _frag__as__DowngradeChangeVariables_billable_features = _frag__as__DowngradeChangeVariables.billable_features()
    _frag__as__DowngradeChangeVariables_billable_features.feature_id()
    _frag__as__DowngradeChangeVariables_billable_features.quantity()
    _frag__as__DowngradeChangeVariables_addons = _frag__as__DowngradeChangeVariables.addons()
    _frag__as__DowngradeChangeVariables_addons.addon_ref_id()
    _frag__as__DowngradeChangeVariables_addons.quantity()
    _frag__as__DowngradeChangeVariables_price_overrides = _frag__as__DowngradeChangeVariables.price_overrides()
    _frag__as__DowngradeChangeVariables_price_overrides.plan_ref_id()
    _frag__as__DowngradeChangeVariables_price_overrides.addon_ref_id()
    _frag__as__DowngradeChangeVariables_price_overrides.feature_id()
    _frag__as__BillingPeriodChangeVariables = _frag.__as__(_schema.BillingPeriodChangeVariables)
    _frag__as__BillingPeriodChangeVariables.billing_period()
    _frag__as__UnitAmountChangeVariables = _frag.__as__(_schema.UnitAmountChangeVariables)
    _frag__as__UnitAmountChangeVariables.new_unit_amount()
    _frag__as__UnitAmountChangeVariables.feature_id()
    _frag__as__AddonChangeVariables = _frag.__as__(_schema.AddonChangeVariables)
    _frag__as__AddonChangeVariables.addon_ref_id()
    _frag__as__AddonChangeVariables.new_quantity()
    _frag__as__PlanPriceOverrideChangeVariables = _frag.__as__(_schema.PlanPriceOverrideChangeVariables)
    _frag__as__PlanPriceOverrideChangeVariables.plan_ref_id()
    _frag__as__PlanPriceOverrideChangeVariables.feature_id()
    _frag__as__AddonPriceOverrideChangeVariables = _frag.__as__(_schema.AddonPriceOverrideChangeVariables)
    _frag__as__AddonPriceOverrideChangeVariables.addon_ref_id()
    _frag__as__AddonPriceOverrideChangeVariables.feature_id()
    return _frag


def fragment_credit_grant_fragment():
    _frag = sgqlc.operation.Fragment(_schema.CreditGrant, 'CreditGrantFragment')
    _frag.grant_id()
    _frag.amount()
    _frag.comment()
    _frag.currency_id()
    _frag.customer_id()
    _frag.display_name()
    _frag.effective_at()
    _frag.expire_at()
    _frag.grant_type()
    _frag.priority()
    _frag.consumed_amount()
    _frag_cost = _frag.cost()
    _frag_cost.amount()
    _frag_cost.currency()
    _frag.created_at()
    _frag.updated_at()
    _frag.resource_id()
    _frag.additional_meta_data()
    return _frag


def fragment_credits_balance_summary_fragment():
    _frag = sgqlc.operation.Fragment(_schema.CreditBalanceSummary, 'CreditsBalanceSummaryFragment')
    _frag.customer_id()
    _frag_balances = _frag.balances()
    _frag_balances_currency = _frag_balances.currency()
    _frag_balances_currency.currency_id()
    _frag_balances_currency.display_name()
    _frag_balances_currency.symbol()
    _frag_balances.current_balance()
    _frag_balances.total_consumed()
    _frag_balances.total_granted()
    return _frag


class Fragment:
    addon_dependency_fragment = fragment_addon_dependency_fragment()
    addon_fragment = fragment_addon_fragment()
    apply_subscription_fragment = fragment_apply_subscription_fragment()
    checkout_configuration_fragment = fragment_checkout_configuration_fragment()
    checkout_state_fragment = fragment_checkout_state_fragment()
    coupon_fragment = fragment_coupon_fragment()
    credit_grant_fragment = fragment_credit_grant_fragment()
    credits_balance_summary_fragment = fragment_credits_balance_summary_fragment()
    customer_fragment = fragment_customer_fragment()
    customer_portal_billing_information_fragment = fragment_customer_portal_billing_information_fragment()
    customer_portal_configuration_fragment = fragment_customer_portal_configuration_fragment()
    customer_portal_entitlement_fragment = fragment_customer_portal_entitlement_fragment()
    customer_portal_fragment = fragment_customer_portal_fragment()
    customer_portal_promotional_entitlement_fragment = fragment_customer_portal_promotional_entitlement_fragment()
    customer_portal_subscription_addon_fragment = fragment_customer_portal_subscription_addon_fragment()
    customer_portal_subscription_fragment = fragment_customer_portal_subscription_fragment()
    customer_portal_subscription_price_fragment = fragment_customer_portal_subscription_price_fragment()
    customer_portal_subscription_scheduled_update_data_fragment = fragment_customer_portal_subscription_scheduled_update_data_fragment()
    customer_resource_fragment = fragment_customer_resource_fragment()
    customer_statistics_fragment = fragment_customer_statistics_fragment()
    customer_with_subscriptions_fragment = fragment_customer_with_subscriptions_fragment()
    entitlement_fragment = fragment_entitlement_fragment()
    entitlement_usage_updated = fragment_entitlement_usage_updated()
    entitlements_updated_payload = fragment_entitlements_updated_payload()
    feature_fragment = fragment_feature_fragment()
    font_variant_fragment = fragment_font_variant_fragment()
    immediate_subscription_preview_invoice_fragment = fragment_immediate_subscription_preview_invoice_fragment()
    layout_configuration_fragment = fragment_layout_configuration_fragment()
    mock_paywall_addon_dependency_fragment = fragment_mock_paywall_addon_dependency_fragment()
    mock_paywall_addon_fragment = fragment_mock_paywall_addon_fragment()
    mock_paywall_package_entitlement_fragment = fragment_mock_paywall_package_entitlement_fragment()
    mock_paywall_plan_compatible_package_groups_fragment = fragment_mock_paywall_plan_compatible_package_groups_fragment()
    mock_paywall_plan_fragment = fragment_mock_paywall_plan_fragment()
    mock_paywall_price_fragment = fragment_mock_paywall_price_fragment()
    overage_price_fragment = fragment_overage_price_fragment()
    package_entitlement_fragment = fragment_package_entitlement_fragment()
    package_published_payload = fragment_package_published_payload()
    page_info_fragment = fragment_page_info_fragment()
    paywall_calculated_price_points_fragment = fragment_paywall_calculated_price_points_fragment()
    paywall_configuration_fragment = fragment_paywall_configuration_fragment()
    paywall_currency_fragment = fragment_paywall_currency_fragment()
    paywall_fragment = fragment_paywall_fragment()
    plan_compatible_package_groups_fragment = fragment_plan_compatible_package_groups_fragment()
    plan_fragment = fragment_plan_fragment()
    price_fragment = fragment_price_fragment()
    price_tier_fragment = fragment_price_tier_fragment()
    product_fragment = fragment_product_fragment()
    promotional_entitlement_fragment = fragment_promotional_entitlement_fragment()
    provision_customer_fragment = fragment_provision_customer_fragment()
    provision_subscription_fragment = fragment_provision_subscription_fragment()
    report_usage_fragment = fragment_report_usage_fragment()
    reset_period_configuration_fragment = fragment_reset_period_configuration_fragment()
    schedule_variables_fragment = fragment_schedule_variables_fragment()
    slim_customer_fragment = fragment_slim_customer_fragment()
    slim_subscription_fragment = fragment_slim_subscription_fragment()
    slim_subscription_fragment_v2 = fragment_slim_subscription_fragment_v2()
    subscription_fragment = fragment_subscription_fragment()
    subscription_future_update_data = fragment_subscription_future_update_data()
    subscription_invoice_fragment = fragment_subscription_invoice_fragment()
    subscription_invoice_preview_fragment = fragment_subscription_invoice_preview_fragment()
    subscription_preview_fragment = fragment_subscription_preview_fragment()
    subscription_preview_invoice_fragment = fragment_subscription_preview_invoice_fragment()
    subscription_preview_v2_fragment = fragment_subscription_preview_v2_fragment()
    subscription_query_fragment = fragment_subscription_query_fragment()
    subscription_scheduled_update_data = fragment_subscription_scheduled_update_data()
    subscription_trial_configuration_fragment = fragment_subscription_trial_configuration_fragment()
    total_price_fragment = fragment_total_price_fragment()
    typography_configuration_fragment = fragment_typography_configuration_fragment()
    usage_history_fragment = fragment_usage_history_fragment()
    usage_history_v2_fragment = fragment_usage_history_v2_fragment()
    usage_updated_fragment = fragment_usage_updated_fragment()


def mutation_provision_customer():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='ProvisionCustomer', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.ProvisionCustomerInput))))
    _op_provision_customer = _op.provision_customer(input=sgqlc.types.Variable('input'))
    _op_provision_customer.__fragment__(fragment_provision_customer_fragment())
    return _op


def mutation_import_customer_bulk():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='ImportCustomerBulk', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.ImportCustomerBulkInput))))
    _op.import_customers_bulk(input=sgqlc.types.Variable('input'))
    return _op


def mutation_import_customer():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='ImportCustomer', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.ImportCustomerInput))))
    _op_import_customer = _op.import_one_customer(input=sgqlc.types.Variable('input'), __alias__='import_customer')
    _op_import_customer.__fragment__(fragment_slim_customer_fragment())
    return _op


def mutation_update_customer():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='UpdateCustomer', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.UpdateCustomerInput))))
    _op_update_customer = _op.update_one_customer(input=sgqlc.types.Variable('input'), __alias__='update_customer')
    _op_update_customer.__fragment__(fragment_slim_customer_fragment())
    return _op


def mutation_detach_customer_payment_method():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='DetachCustomerPaymentMethod', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.DetachCustomerPaymentMethodInput))))
    _op_detach_customer_payment_method = _op.detach_customer_payment_method(input=sgqlc.types.Variable('input'))
    _op_detach_customer_payment_method.__fragment__(fragment_slim_customer_fragment())
    return _op


def mutation_grant_promotional_entitlements():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='GrantPromotionalEntitlements', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.GrantPromotionalEntitlementsInput))))
    _op_grant_promotional_entitlements = _op.grant_promotional_entitlements(input=sgqlc.types.Variable('input'))
    _op_grant_promotional_entitlements.__fragment__(fragment_promotional_entitlement_fragment())
    return _op


def mutation_revoke_promotional_entitlement():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='RevokePromotionalEntitlement', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.RevokePromotionalEntitlementInput))))
    _op_revoke_promotional_entitlement = _op.revoke_promotional_entitlement(input=sgqlc.types.Variable('input'))
    _op_revoke_promotional_entitlement.id()
    return _op


def mutation_provision_subscription():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='ProvisionSubscription', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.ProvisionSubscriptionInput))))
    _op_provision_subscription = _op.provision_subscription_v2(input=sgqlc.types.Variable('input'), __alias__='provision_subscription')
    _op_provision_subscription.__fragment__(fragment_provision_subscription_fragment())
    return _op


def mutation_apply_subscription():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='ApplySubscription', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.ApplySubscriptionInput))))
    _op_apply_subscription = _op.apply_subscription(input=sgqlc.types.Variable('input'))
    _op_apply_subscription.__fragment__(fragment_apply_subscription_fragment())
    return _op


def mutation_import_subscriptions_bulk():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='ImportSubscriptionsBulk', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.ImportSubscriptionsBulkInput))))
    _op.import_subscriptions_bulk(input=sgqlc.types.Variable('input'))
    return _op


def mutation_update_subscription():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='UpdateSubscription', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.UpdateSubscriptionInput))))
    _op_update_subscription = _op.update_one_subscription(input=sgqlc.types.Variable('input'), __alias__='update_subscription')
    _op_update_subscription.__fragment__(fragment_slim_subscription_fragment())
    return _op


def mutation_cancel_subscription():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='CancelSubscription', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.SubscriptionCancellationInput))))
    _op_cancel_subscription = _op.cancel_subscription(input=sgqlc.types.Variable('input'))
    _op_cancel_subscription.__fragment__(fragment_slim_subscription_fragment())
    return _op


def mutation_estimate_subscription():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='EstimateSubscription', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.EstimateSubscriptionInput))))
    _op_estimate_subscription = _op.estimate_subscription(input=sgqlc.types.Variable('input'))
    _op_estimate_subscription.__fragment__(fragment_subscription_preview_fragment())
    return _op


def mutation_estimate_subscription_update():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='EstimateSubscriptionUpdate', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.EstimateSubscriptionUpdateInput))))
    _op_estimate_subscription_update = _op.estimate_subscription_update(input=sgqlc.types.Variable('input'))
    _op_estimate_subscription_update.__fragment__(fragment_subscription_preview_fragment())
    return _op


def mutation_preview_subscription():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='PreviewSubscription', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.PreviewSubscriptionInput))))
    _op_preview_subscription = _op.preview_subscription(input=sgqlc.types.Variable('input'))
    _op_preview_subscription.__fragment__(fragment_subscription_preview_v2_fragment())
    return _op


def mutation_preview_next_invoice():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='PreviewNextInvoice', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.PreviewNextInvoiceInput))))
    _op_preview_next_invoice = _op.preview_next_invoice(input=sgqlc.types.Variable('input'))
    _op_preview_next_invoice.__fragment__(fragment_subscription_invoice_preview_fragment())
    return _op


def mutation_cancel_subscription_updates():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='CancelSubscriptionUpdates', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.SubscriptionUpdateScheduleCancellationInput))))
    _op.cancel_schedule(input=sgqlc.types.Variable('input'))
    return _op


def mutation_report_usage():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='ReportUsage', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.ReportUsageInput))))
    _op_report_usage = _op.report_usage(input=sgqlc.types.Variable('input'))
    _op_report_usage.__fragment__(fragment_report_usage_fragment())
    return _op


def mutation_report_usage_bulk():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='ReportUsageBulk', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.ReportUsageBulkInput))))
    _op_report_usage_bulk = _op.report_usage_bulk(input=sgqlc.types.Variable('input'))
    _op_report_usage_bulk.__fragment__(fragment_report_usage_fragment())
    return _op


def mutation_report_event():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='ReportEvent', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.UsageEventsReportInput))))
    _op.report_event(events=sgqlc.types.Variable('input'))
    return _op


def mutation_report_entitlement_check_requested():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='ReportEntitlementCheckRequested', variables=dict(entitlementCheckRequested=sgqlc.types.Arg(sgqlc.types.non_null(_schema.EntitlementCheckRequested))))
    _op.report_entitlement_check_requested(entitlement_check_requested=sgqlc.types.Variable('entitlementCheckRequested'))
    return _op


def mutation_create_subscription():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='CreateSubscription', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.SubscriptionInput))))
    _op_create_subscription = _op.create_subscription(subscription=sgqlc.types.Variable('input'))
    _op_create_subscription.__fragment__(fragment_slim_subscription_fragment())
    return _op


def mutation_migrate_subscription_to_latest():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='MigrateSubscriptionToLatest', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.SubscriptionMigrationInput))))
    _op_migrate_subscription_to_latest = _op.migrate_subscription_to_latest(input=sgqlc.types.Variable('input'))
    _op_migrate_subscription_to_latest.subscription_id()
    return _op


def mutation_archive_customer():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='ArchiveCustomer', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.ArchiveCustomerInput))))
    _op_archive_customer = _op.archive_customer(input=sgqlc.types.Variable('input'))
    _op_archive_customer.customer_id()
    return _op


def mutation_unarchive_customer():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='UnarchiveCustomer', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.UnarchiveCustomerInput))))
    _op_unarchive_customer = _op.unarchive_customer(input=sgqlc.types.Variable('input'))
    _op_unarchive_customer.__fragment__(fragment_slim_customer_fragment())
    return _op


def mutation_transfer_subscription():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='TransferSubscription', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.TransferSubscriptionInput))))
    _op_transfer_subscription = _op.transfer_subscription(input=sgqlc.types.Variable('input'))
    _op_transfer_subscription.__fragment__(fragment_slim_subscription_fragment())
    return _op


def mutation_delegate_subscription_to_customer():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='DelegateSubscriptionToCustomer', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.DelegateSubscriptionToCustomerInput))))
    _op_delegate_subscription_to_customer = _op.delegate_subscription_to_customer(input=sgqlc.types.Variable('input'))
    _op_delegate_subscription_to_customer.__fragment__(fragment_slim_subscription_fragment())
    return _op


def mutation_transfer_subscription_to_resource():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='TransferSubscriptionToResource', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.TransferSubscriptionToResourceInput))))
    _op_transfer_subscription_to_resource = _op.transfer_subscription_to_resource(input=sgqlc.types.Variable('input'))
    _op_transfer_subscription_to_resource.__fragment__(fragment_slim_subscription_fragment())
    return _op


def mutation_grant_credits():
    _op = sgqlc.operation.Operation(_schema_root.mutation_type, name='GrantCredits', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.CreditGrantInput))))
    _op_create_credit_grant = _op.create_credit_grant(input=sgqlc.types.Variable('input'))
    _op_create_credit_grant.__fragment__(fragment_credit_grant_fragment())
    return _op


class Mutation:
    apply_subscription = mutation_apply_subscription()
    archive_customer = mutation_archive_customer()
    cancel_subscription = mutation_cancel_subscription()
    cancel_subscription_updates = mutation_cancel_subscription_updates()
    create_subscription = mutation_create_subscription()
    delegate_subscription_to_customer = mutation_delegate_subscription_to_customer()
    detach_customer_payment_method = mutation_detach_customer_payment_method()
    estimate_subscription = mutation_estimate_subscription()
    estimate_subscription_update = mutation_estimate_subscription_update()
    grant_credits = mutation_grant_credits()
    grant_promotional_entitlements = mutation_grant_promotional_entitlements()
    import_customer = mutation_import_customer()
    import_customer_bulk = mutation_import_customer_bulk()
    import_subscriptions_bulk = mutation_import_subscriptions_bulk()
    migrate_subscription_to_latest = mutation_migrate_subscription_to_latest()
    preview_next_invoice = mutation_preview_next_invoice()
    preview_subscription = mutation_preview_subscription()
    provision_customer = mutation_provision_customer()
    provision_subscription = mutation_provision_subscription()
    report_entitlement_check_requested = mutation_report_entitlement_check_requested()
    report_event = mutation_report_event()
    report_usage = mutation_report_usage()
    report_usage_bulk = mutation_report_usage_bulk()
    revoke_promotional_entitlement = mutation_revoke_promotional_entitlement()
    transfer_subscription = mutation_transfer_subscription()
    transfer_subscription_to_resource = mutation_transfer_subscription_to_resource()
    unarchive_customer = mutation_unarchive_customer()
    update_customer = mutation_update_customer()
    update_subscription = mutation_update_subscription()


def query_get_customer_by_id():
    _op = sgqlc.operation.Operation(_schema_root.query_type, name='GetCustomerById', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.GetCustomerByRefIdInput))))
    _op_get_customer_by_ref_id = _op.get_customer_by_ref_id(input=sgqlc.types.Variable('input'))
    _op_get_customer_by_ref_id.__fragment__(fragment_customer_with_subscriptions_fragment())
    return _op


def query_get_customer_statistics():
    _op = sgqlc.operation.Operation(_schema_root.query_type, name='GetCustomerStatistics', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.GetCustomerByRefIdInput))))
    _op_get_customer_by_ref_id = _op.get_customer_by_ref_id(input=sgqlc.types.Variable('input'))
    _op_get_customer_by_ref_id.__fragment__(fragment_customer_statistics_fragment())
    return _op


def query_get_active_subscriptions():
    _op = sgqlc.operation.Operation(_schema_root.query_type, name='GetActiveSubscriptions', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.GetActiveSubscriptionsInput))))
    _op_get_active_subscriptions = _op.get_active_subscriptions(input=sgqlc.types.Variable('input'))
    _op_get_active_subscriptions.__fragment__(fragment_subscription_fragment())
    return _op


def query_get_active_subscriptions_list():
    _op = sgqlc.operation.Operation(_schema_root.query_type, name='GetActiveSubscriptionsList', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.GetActiveSubscriptionsInput))))
    _op_get_active_subscriptions = _op.get_active_subscriptions(input=sgqlc.types.Variable('input'))
    _op_get_active_subscriptions.__fragment__(fragment_slim_subscription_fragment_v2())
    return _op


def query_get_subscriptions():
    _op = sgqlc.operation.Operation(_schema_root.query_type, name='GetSubscriptions', variables=dict(filter=sgqlc.types.Arg(_schema.SubscriptionQueryFilter), paging=sgqlc.types.Arg(_schema.CursorPaging), sorting=sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(_schema.SubscriptionQuerySort)))))
    _op_subscriptions = _op.subscriptions(filter=sgqlc.types.Variable('filter'), paging=sgqlc.types.Variable('paging'), sorting=sgqlc.types.Variable('sorting'))
    _op_subscriptions_edges = _op_subscriptions.edges()
    _op_subscriptions_edges_node = _op_subscriptions_edges.node()
    _op_subscriptions_edges_node.__fragment__(fragment_subscription_query_fragment())
    _op_subscriptions_page_info = _op_subscriptions.page_info()
    _op_subscriptions_page_info.__fragment__(fragment_page_info_fragment())
    return _op


def query_get_subscription():
    _op = sgqlc.operation.Operation(_schema_root.query_type, name='GetSubscription', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.GetSubscriptionInput))))
    _op_get_subscription = _op.get_subscription(input=sgqlc.types.Variable('input'))
    _op_get_subscription.__fragment__(fragment_subscription_fragment())
    return _op


def query_get_coupons():
    _op = sgqlc.operation.Operation(_schema_root.query_type, name='GetCoupons')
    _op_coupons = _op.coupons(filter={'status': {'eq': 'ACTIVE'}}, paging={'first': 50})
    _op_coupons_edges = _op_coupons.edges()
    _op_coupons_edges_node = _op_coupons_edges.node()
    _op_coupons_edges_node.__fragment__(fragment_coupon_fragment())
    return _op


def query_get_paywall():
    _op = sgqlc.operation.Operation(_schema_root.query_type, name='GetPaywall', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.GetPaywallInput))))
    _op_paywall = _op.paywall(input=sgqlc.types.Variable('input'))
    _op_paywall.__fragment__(fragment_paywall_fragment())
    return _op


def query_get_entitlements():
    _op = sgqlc.operation.Operation(_schema_root.query_type, name='GetEntitlements', variables=dict(query=sgqlc.types.Arg(sgqlc.types.non_null(_schema.FetchEntitlementsQuery))))
    _op_entitlements = _op.cached_entitlements(query=sgqlc.types.Variable('query'), __alias__='entitlements')
    _op_entitlements.__fragment__(fragment_entitlement_fragment())
    return _op


def query_get_entitlement():
    _op = sgqlc.operation.Operation(_schema_root.query_type, name='GetEntitlement', variables=dict(query=sgqlc.types.Arg(sgqlc.types.non_null(_schema.FetchEntitlementQuery))))
    _op_entitlement = _op.entitlement(query=sgqlc.types.Variable('query'))
    _op_entitlement.__fragment__(fragment_entitlement_fragment())
    return _op


def query_get_products():
    _op = sgqlc.operation.Operation(_schema_root.query_type, name='GetProducts')
    _op_products = _op.products(paging={'first': 20})
    _op_products_edges = _op_products.edges()
    _op_products_edges_node = _op_products_edges.node()
    _op_products_edges_node.__fragment__(fragment_product_fragment())
    return _op


def query_get_sdk_configuration():
    _op = sgqlc.operation.Operation(_schema_root.query_type, name='GetSdkConfiguration')
    _op_sdk_configuration = _op.sdk_configuration()
    _op_sdk_configuration.sentry_dsn()
    _op_sdk_configuration.is_widget_watermark_enabled()
    return _op


def query_get_customer_portal_by_ref_id():
    _op = sgqlc.operation.Operation(_schema_root.query_type, name='GetCustomerPortalByRefId', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.CustomerPortalInput))))
    _op_customer_portal = _op.customer_portal(input=sgqlc.types.Variable('input'))
    _op_customer_portal.__fragment__(fragment_customer_portal_fragment())
    return _op


def query_get_checkout_state():
    _op = sgqlc.operation.Operation(_schema_root.query_type, name='GetCheckoutState', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.CheckoutStateInput))))
    _op_checkout_state = _op.checkout_state(input=sgqlc.types.Variable('input'))
    _op_checkout_state.__fragment__(fragment_checkout_state_fragment())
    return _op


def query_get_mock_paywall():
    _op = sgqlc.operation.Operation(_schema_root.query_type, name='GetMockPaywall', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.GetPaywallInput))))
    _op_mock_paywall = _op.mock_paywall(input=sgqlc.types.Variable('input'))
    _op_mock_paywall_plans = _op_mock_paywall.plans()
    _op_mock_paywall_plans.__fragment__(fragment_mock_paywall_plan_fragment())
    _op_mock_paywall_configuration = _op_mock_paywall.configuration()
    _op_mock_paywall_configuration.__fragment__(fragment_paywall_configuration_fragment())
    return _op


def query_get_usage_history():
    _op = sgqlc.operation.Operation(_schema_root.query_type, name='GetUsageHistory', variables=dict(usageHistoryInput=sgqlc.types.Arg(sgqlc.types.non_null(_schema.UsageHistoryInput))))
    _op_usage_history = _op.usage_history(usage_history_input=sgqlc.types.Variable('usageHistoryInput'))
    _op_usage_history.__fragment__(fragment_usage_history_fragment())
    return _op


def query_get_usage_history_v2():
    _op = sgqlc.operation.Operation(_schema_root.query_type, name='GetUsageHistoryV2', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.UsageHistoryV2Input))))
    _op_usage_history_v2 = _op.usage_history_v2(input=sgqlc.types.Variable('input'))
    _op_usage_history_v2.__fragment__(fragment_usage_history_v2_fragment())
    return _op


def query_get_credit_balance():
    _op = sgqlc.operation.Operation(_schema_root.query_type, name='GetCreditBalance', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.CreditBalanceSummaryInput))))
    _op_credit_balance_summary = _op.credit_balance_summary(input=sgqlc.types.Variable('input'))
    _op_credit_balance_summary.__fragment__(fragment_credits_balance_summary_fragment())
    return _op


def query_get_credit_grants():
    _op = sgqlc.operation.Operation(_schema_root.query_type, name='GetCreditGrants', variables=dict(input=sgqlc.types.Arg(sgqlc.types.non_null(_schema.GetCreditGrantsInput))))
    _op_credit_grants = _op.credit_grants(input=sgqlc.types.Variable('input'))
    _op_credit_grants.__fragment__(fragment_credit_grant_fragment())
    return _op


class Query:
    get_active_subscriptions = query_get_active_subscriptions()
    get_active_subscriptions_list = query_get_active_subscriptions_list()
    get_checkout_state = query_get_checkout_state()
    get_coupons = query_get_coupons()
    get_credit_balance = query_get_credit_balance()
    get_credit_grants = query_get_credit_grants()
    get_customer_by_id = query_get_customer_by_id()
    get_customer_portal_by_ref_id = query_get_customer_portal_by_ref_id()
    get_customer_statistics = query_get_customer_statistics()
    get_entitlement = query_get_entitlement()
    get_entitlements = query_get_entitlements()
    get_mock_paywall = query_get_mock_paywall()
    get_paywall = query_get_paywall()
    get_products = query_get_products()
    get_sdk_configuration = query_get_sdk_configuration()
    get_subscription = query_get_subscription()
    get_subscriptions = query_get_subscriptions()
    get_usage_history = query_get_usage_history()
    get_usage_history_v2 = query_get_usage_history_v2()


def subscription_on_entitlements_updated():
    _op = sgqlc.operation.Operation(_schema_root.subscription_type, name='OnEntitlementsUpdated')
    _op_entitlements_updated = _op.entitlements_updated()
    _op_entitlements_updated.__fragment__(fragment_entitlements_updated_payload())
    return _op


def subscription_on_usage_updated():
    _op = sgqlc.operation.Operation(_schema_root.subscription_type, name='OnUsageUpdated')
    _op_usage_updated = _op.usage_updated()
    _op_usage_updated.__fragment__(fragment_entitlement_usage_updated())
    return _op


def subscription_on_package_published():
    _op = sgqlc.operation.Operation(_schema_root.subscription_type, name='OnPackagePublished')
    _op_package_published = _op.package_published()
    _op_package_published.__fragment__(fragment_package_published_payload())
    return _op


class Subscription:
    on_entitlements_updated = subscription_on_entitlements_updated()
    on_package_published = subscription_on_package_published()
    on_usage_updated = subscription_on_usage_updated()


class Operations:
    fragment = Fragment
    mutation = Mutation
    query = Query
    subscription = Subscription
