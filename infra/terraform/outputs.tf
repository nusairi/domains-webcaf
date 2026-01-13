output "acr_login_server" {
  value = azurerm_container_registry.main.login_server
}

output "key_vault_name" {
  value = azurerm_key_vault.main.name
}

output "postgres_fqdn" {
  value = azurerm_postgresql_flexible_server.main.fqdn
}

output "postgres_admin_username" {
  value = azurerm_postgresql_flexible_server.main.administrator_login
}

output "postgres_admin_password_secret_id" {
  value     = azurerm_key_vault_secret.postgres_admin_password.id
  sensitive = true
}

output "container_app_fqdn" {
  value = azurerm_container_app.main.latest_revision_fqdn
}
