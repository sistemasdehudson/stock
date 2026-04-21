import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """
    Post-migración stock_ux 19.0.1.4.0
    Desactiva vistas de módulos desinstalados que no existen en v19.
    Se hace en post-migrate para que corra después de que todos los
    módulos carguen y antes de que el servidor levante.
    """
    _logger.info("stock_ux post-migrate: desactivando vistas de módulos desinstalados")

    vistas = [
        # stock_voucher
        ('stock_voucher', 'view_move_tree'),
        ('stock_voucher', 'view_picking_form'),
        ('stock_voucher', 'view_picking_type_form'),
        ('stock_voucher', 'view_print_stock_voucher_form'),
        ('stock_voucher', 'view_stock_picking_voucher_form'),
        ('stock_voucher', 'view_stock_picking_voucher_tree'),
        ('stock_voucher', 'vpicktree'),
        # stock_reserve
        ('stock_reserve', 'product_product_form_view_reservation_button'),
        ('stock_reserve', 'product_template_form_view_reservation_button'),
        # stock_batch_picking_ux
        ('stock_batch_picking_ux', 'custom_label_transfer_template_view_pdf'),
        ('stock_batch_picking_ux', 'custom_label_transfer_template_view_zpl'),
        ('stock_batch_picking_ux', 'vpicktree'),
        # stock_picking_purchase_order_link
        ('stock_picking_purchase_order_link', 'view_picking_form'),
        # stock_picking_sale_order_link
        ('stock_picking_sale_order_link', 'view_picking_form'),
        # stock_picking_show_return
        ('stock_picking_show_return', 'view_picking_form'),
        # purchase_stock_ux
        ('purchase_stock_ux', 'purchase_order_line_search'),
        ('purchase_stock_ux', 'purchase_order_line_tree'),
        # sale_stock_picking_note
        ('sale_stock_picking_note', 'view_picking_form'),
        ('sale_stock_picking_note', 'view_order_form'),
        ('sale_stock_picking_note', 'view_partner_form_inherit_partner_picking_note'),
        ('sale_stock_picking_note', 'report_delivery_document_customer_note'),
        # l10n_ar_withholding_ux
        ('l10n_ar_withholding_ux', 'report_payment_receipt_document'),
    ]

    total = 0
    for module, xmlid in vistas:
        cr.execute("""
            UPDATE ir_ui_view v
            SET active = False
            FROM ir_model_data d
            WHERE d.res_id = v.id
              AND d.model = 'ir.ui.view'
              AND d.module = %s
              AND d.name = %s
              AND v.active = True
        """, (module, xmlid))
        if cr.rowcount > 0:
            _logger.info(f"  ✓ {module}.{xmlid} desactivada")
            total += 1

    _logger.info(f"stock_ux post-migrate: {total} vistas desactivadas")