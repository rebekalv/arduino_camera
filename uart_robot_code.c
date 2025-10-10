#include "nrf_drv_uart.h"
#include "nrf_delay.h"
#include "nrf_log.h"
#include "nrf_log_ctrl.h"
#include "nrf_log_default_backends.h"

#define UART_TX_PIN 6   // adjust to your board
#define UART_RX_PIN 8
#define UART_BAUDRATE NRF_UART_BAUDRATE_115200

static const nrf_drv_uart_t uart = NRF_DRV_UART_INSTANCE(0);

void uart_init(void)
{
    nrf_drv_uart_config_t config = NRF_DRV_UART_DEFAULT_CONFIG;
    config.pseltxd = UART_TX_PIN;
    config.pselrxd = UART_RX_PIN;
    config.baudrate = UART_BAUDRATE;
    config.hwfc = NRF_UART_HWFC_DISABLED;

    APP_ERROR_CHECK(nrf_drv_uart_init(&uart, &config, NULL));

    NRF_LOG_INFO("UART initialized");
    NRF_LOG_FLUSH();
}

void uart_receive_loop(void)
{
    uint8_t byte;
    while (true)
    {
        if (nrf_drv_uart_rx(&uart, &byte, 1) == NRF_SUCCESS)
        {
            // Print received byte
            NRF_LOG_INFO("Received: %d", byte);
            NRF_LOG_FLUSH();
        }
    }
}

int main(void)
{
    APP_ERROR_CHECK(NRF_LOG_INIT(NULL));
    NRF_LOG_DEFAULT_BACKENDS_INIT();

    uart_init();
    
    NRF_LOG_INFO("Waiting for UART data...");
    NRF_LOG_FLUSH();

    uart_receive_loop();
}

