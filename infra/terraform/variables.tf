variable "location" {
  type    = string
  default = "uksouth"
}

variable "resource_group_name" {
  type    = string
  default = "MHCLGPoc"
}

variable "name_prefix" {
  type    = string
  default = "webcaflocalpoc"
}

variable "postgres_admin_user" {
  type    = string
  default = "webcafadmin"
}

variable "postgres_version" {
  type    = string
  default = "15"
}

variable "postgres_sku_name" {
  type    = string
  default = "B_Standard_B1ms"
}

variable "postgres_storage_mb" {
  type    = number
  default = 32768
}

variable "domain_name" {
  type    = string
  default = "webcaflocalpoc.proudcliff-075198f5.uksouth.azurecontainerapps.io"
}

variable "container_image" {
  type        = string
  default     = null
  description = "Optional full image reference; when null, uses ACR webcaf:latest."
}

variable "oidc_client_id" {
  type = string
}

variable "oidc_client_secret" {
  type      = string
  sensitive = true
}

variable "oidc_client_assertion_private_key" {
  type      = string
  sensitive = true
  default   = ""
}

variable "oidc_client_assertion_kid" {
  type    = string
  default = ""
}

variable "oidc_op_authorization_endpoint" {
  type    = string
  default = "https://login.microsoftonline.com/2062bf1d-f9d8-4916-afd0-ca3624f1b2be/oauth2/v2.0/authorize"
}

variable "oidc_op_token_endpoint" {
  type    = string
  default = "https://login.microsoftonline.com/2062bf1d-f9d8-4916-afd0-ca3624f1b2be/oauth2/v2.0/token"
}

variable "oidc_op_user_endpoint" {
  type    = string
  default = "https://graph.microsoft.com/oidc/userinfo"
}

variable "oidc_op_jwks_endpoint" {
  type    = string
  default = "https://login.microsoftonline.com/2062bf1d-f9d8-4916-afd0-ca3624f1b2be/discovery/v2.0/keys"
}

variable "oidc_op_logout_endpoint" {
  type    = string
  default = "https://login.microsoftonline.com/2062bf1d-f9d8-4916-afd0-ca3624f1b2be/oauth2/v2.0/logout"
}

variable "oidc_rp_scopes" {
  type    = string
  default = "openid email profile"
}

variable "oidc_rp_sign_algo" {
  type    = string
  default = "RS256"
}

variable "oidc_token_auth_method" {
  type    = string
  default = "client_secret_basic"
}

variable "oidc_user_agent" {
  type    = string
  default = "webcaf/1.0"
}

variable "oidc_client_assertion_alg" {
  type    = string
  default = "RS256"
}

variable "webapp_name" {
  type    = string
  default = "webcaflocalpoc"
}

variable "sso_mode" {
  type    = string
  default = "external"
}
