#include <stdio.h>
#include <yaml.h>

/* Define an enum for the current key */
typedef enum {
    KEY,
    NAME,
    DETAILS,
    CITATION,
    URLS,
    FILES,
    LICENSE,
    SIZE
} current_key;

/* Define a struct to hold the data */
typedef struct dataset {
  char* name;
  char* details;
  char* citation;
  char** urls;
  int num_urls;
  char*** files;
  int* num_files;
  char* license;
  int size;
} dataset;

/* Initialize an array of datasets */
dataset datasets[100];
int dataset_count = 0;
int max_urls = 256;
int main(void)
{
  FILE *file = fopen("test.yaml", "r");
  if(file == NULL) {
    fputs("Failed to open file!\n", stderr);
    return 1;
  }
  yaml_parser_t parser;
  yaml_event_t event;
  
  current_key state = KEY;
  /* Initialize parser */
  if(!yaml_parser_initialize(&parser)) {
    fputs("Failed to initialize parser!\n", stderr);
    return 1;
  }
  
  /* Set input file */
  yaml_parser_set_input_file(&parser, file);
  
  /* Start parsing */
  while(1) {
    if (!yaml_parser_parse(&parser, &event)) {
      printf("Parser error %d\n", parser.error);
      return 1;
    }
    
    /* Break if we reach the end of the document */
    if (event.type == YAML_DOCUMENT_END_EVENT) {
      yaml_event_delete(&event);
      break;
    }
    
    /* Handle different event types */
    if (event.type == YAML_SCALAR_EVENT) {
      if (state == KEY) {
	if (strcmp((char*)event.data.scalar.value, "name") == 0) {
	  state = NAME;
	} else if (strcmp((char*)event.data.scalar.value, "details") == 0) {
	  state = DETAILS;
	} else if (strcmp((char*)event.data.scalar.value, "citation") == 0) {
	  state = CITATION;
	} else if (strcmp((char*)event.data.scalar.value, "urls") == 0) {
	  state = URLS;
	} else if (strcmp((char*)event.data.scalar.value, "files") == 0) {
	  state = FILES;
	} else if (strcmp((char*)event.data.scalar.value, "license") == 0) {
	  state = LICENSE;
	} else if (strcmp((char*)event.data.scalar.value, "size") == 0) {
	  state = SIZE;
	}
      } else if (state == NAME) {
	datasets[dataset_count].name = (char *)malloc((event.data.scalar.length + 1) * sizeof(char));
	strcpy(datasets[dataset_count].name, (char *)event.data.scalar.value);
	state = KEY;
      } else if (state == DETAILS) {
	datasets[dataset_count].details = (char *)malloc((event.data.scalar.length + 1) * sizeof(char));
	strcpy(datasets[dataset_count].details, (char *)event.data.scalar.value);
	state = KEY;
      } else if (state == CITATION) {
	datasets[dataset_count].citation = (char *)malloc((event.data.scalar.length + 1) * sizeof(char));
	strcpy(datasets[dataset_count].citation, (char *)event.data.scalar.value);
	state = KEY;
      } else if (state == URLS) {
	datasets[dataset_count].urls = (char **)malloc(max_urls*sizeof(char*));
	while (event.type != YAML_SEQUENCE_END_EVENT) { // loop around layers
	  int url_count = 0;
	  if(event.type == YAML_SCALAR_EVENT) {
	    datasets[dataset_count].urls[url_count] = (char *)malloc((event.data.scalar.length + 1) * sizeof(char));
	    strcpy(datasets[dataset_count].urls, (char *)event.data.scalar.value);
	    url_count++;
	    if(url_count==max_urls) {
	      break;
	    }
	  }
	}
	//
	state = KEY;
      } else if (state == FILES) {
	//datasets[dataset_count].files = (char *)malloc((event.data.scalar.length + 1) * sizeof(char));
	//strcpy(datasets[dataset_count].files, (char *)event.data.scalar.value);
	state = KEY;
      } else if (state == LICENSE) {
	datasets[dataset_count].license = (char *)malloc((event.data.scalar.length + 1) * sizeof(char));
	strcpy(datasets[dataset_count].license, (char *)event.data.scalar.value);
	state = KEY;
      } else if (state == SIZE) {
	datasets[dataset_count].size = atoi((char *)event.data.scalar.value);
	state = KEY;
      }
    } else if (event.type == YAML_SEQUENCE_START_EVENT) {
      /* Ignore */
    } else if (event.type == YAML_SEQUENCE_END_EVENT) {
      /* New dataset */
      dataset_count++;
      state = KEY;
    } else if (event.type == YAML_MAPPING_START_EVENT) {
      /* Ignore */
    } else if (event.type == YAML_MAPPING_END_EVENT) {
      /* Reset key */
      state = KEY;
    }
    
    /* Delete event to avoid memory leaks */
    yaml_event_delete(&event);
  }
  
  /* Cleanup */
  yaml_parser_delete(&parser);
  fclose(file);
  
  /* Print out the data */
  for (int i = 0; i < dataset_count; i++) {
    printf("Dataset %d\n", i);
    printf("  File: %s\n", datasets[i].files);
    printf("  URL: %s\n", datasets[i].urls);
    printf("  Details: %s\n", datasets[i].details);
  }
  
  return 0;
}
