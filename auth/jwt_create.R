#!/usr/bin/env Rscript

#' Firstbeat Sports Cloud API - JWT Generation Script
#'
#' Usage:
#'   Rscript jwt_create.R <consumer_id> <shared_secret>
#'
#' Prerequisites:
#'   install.packages("openssl")
#'   install.packages("jose")

library(openssl)
library(jose)

createJwtToken <- function(consumerId, sharedSecret) {
  tryCatch({
    now <- as.numeric(Sys.time())
    after_five_minutes <- now + 300  # 5 minutes validity

    claim <- jwt_claim(iss = consumerId, iat = now, exp = after_five_minutes)
    secret <- charToRaw(sharedSecret)

    token <- jwt_encode_hmac(claim, secret)
    return(token)
  }, error = function(e) {
    cat("Error generating token:", conditionMessage(e), "\n", file = stderr())
    quit(status = 1)
  })
}

main <- function() {
  args <- commandArgs(trailingOnly = TRUE)

  if (length(args) != 2) {
    cat("Usage: Rscript jwt_create.R <consumer_id> <shared_secret>\n", file = stderr())
    quit(status = 1)
  }

  consumerId <- args[1]
  sharedSecret <- args[2]

  token <- createJwtToken(consumerId, sharedSecret)
  cat("Bearer", token, "\n")
}

main()
