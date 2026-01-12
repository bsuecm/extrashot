/*
 * NDI Source Discovery Tool
 * Uses NDI SDK directly to discover sources on the network
 *
 * Compile: gcc -o ndi_discover ndi_discover.c -lndi -L/usr/local/lib -I/usr/local/include
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <Processing.NDI.Lib.h>

int main(int argc, char* argv[]) {
    int timeout_ms = 5000;  // Default 5 seconds

    // Parse arguments
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-t") == 0 && i + 1 < argc) {
            timeout_ms = atoi(argv[i + 1]) * 1000;
            i++;
        } else if (strcmp(argv[i], "-h") == 0 || strcmp(argv[i], "--help") == 0) {
            printf("Usage: %s [-t timeout_seconds]\n", argv[0]);
            printf("Discovers NDI sources on the network.\n");
            printf("Options:\n");
            printf("  -t <seconds>  Discovery timeout (default: 5)\n");
            printf("\nEnvironment:\n");
            printf("  NDI_EXTRA_IPS  Comma-separated list of extra IPs for discovery\n");
            return 0;
        }
    }

    // Initialize NDI
    if (!NDIlib_initialize()) {
        fprintf(stderr, "ERROR: Failed to initialize NDI library\n");
        return 1;
    }

    // Create finder with extra IPs if set
    NDIlib_find_create_t find_create;
    find_create.show_local_sources = true;
    find_create.p_groups = NULL;

    // Check for extra IPs environment variable
    char* extra_ips = getenv("NDI_EXTRA_IPS");
    find_create.p_extra_ips = extra_ips;

    NDIlib_find_instance_t finder = NDIlib_find_create_v2(&find_create);
    if (!finder) {
        fprintf(stderr, "ERROR: Failed to create NDI finder\n");
        NDIlib_destroy();
        return 1;
    }

    // Wait for sources
    NDIlib_find_wait_for_sources(finder, timeout_ms);

    // Get sources
    uint32_t num_sources = 0;
    const NDIlib_source_t* sources = NDIlib_find_get_current_sources(finder, &num_sources);

    // Output in parseable format
    printf("Found %u devices\n", num_sources);

    for (uint32_t i = 0; i < num_sources; i++) {
        printf("Device %s with 1 configurations\n", sources[i].p_ndi_name);
        if (sources[i].p_url_address && strlen(sources[i].p_url_address) > 0) {
            printf("  address: %s\n", sources[i].p_url_address);
        } else {
            printf("  address: unknown\n");
        }
    }

    // Cleanup
    NDIlib_find_destroy(finder);
    NDIlib_destroy();

    return 0;
}
