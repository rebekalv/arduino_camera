#include "nrf_drv_uart.h"
#include "nrf_delay.h"
#include "nrf_log.h"
#include "nrf_log_ctrl.h"
#include "nrf_log_default_backends.h"

#define UART_TX_PIN 6   // adjust to your board
#define UART_RX_PIN 8
#define UART_BAUDRATE NRF_UART_BAUDRATE_115200
#define NRFX_UARTE_ENABLED 1 

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

void system_init(void)
{
    APP_ERROR_CHECK(NRF_LOG_INIT(NULL));
    NRF_LOG_DEFAULT_BACKENDS_INIT();

    uart_init();
    
    NRF_LOG_INFO("Ready to request data...");
    NRF_LOG_FLUSH();
}

void uart_request_data(void)
{
    uint8_t request_byte = 'r';
    ret_code_t err = nrf_drv_uart_tx(&uart, &request_byte, 1);
    NRF_LOG_INFO("Requested camera data");
    NRF_LOG_FLUSH();
}

bool uart_receive_data(uint8_t *camera_data, size_t length)
{
    ret_code_t err = nrf_drv_uart_rx(&uart, camera_data, length);
    return (err == NRF_SUCCESS);
}

int main(void)
{
    system_init();
    uint8_t camera_data[6];

    while (true)
    {
        uart_request_data();
        if (uart_receive_data(camera_data, 6))
        {
            uint16_t x_start = camera_data[0] | (camera_data[1] << 8);
            uint16_t x_end = camera_data[2] | (camera_data[3] << 8);
            uint16_t distance_cm = camera_data[4] | (camera_data[5] << 8);

            NRF_LOG_INFO("x_start: %d, x_end: %d, distance: %d", x_start, x_end, distance_cm);
            NRF_LOG_FLUSH();
        }
        nrf_delay_ms(1000);  // request periodically
    }
}

