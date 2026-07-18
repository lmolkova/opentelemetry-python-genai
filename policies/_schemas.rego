# Auto-generated from semantic-conventions. Do not edit.
# Regenerate with `make generate-conformance-policies`.
package live_check_advice

import rego.v1

_schema_input_messages := {
  "$defs": {
    "BlobPart": {
      "description": "Represents blob binary data sent inline to the model",
      "properties": {
        "type": {
          "const": "blob",
          "description": "The type of the content captured in this part.",
          "title": "Type",
          "type": "string"
        },
        "mime_type": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "The IANA MIME type of the attached data.",
          "title": "Mime Type"
        },
        "modality": {
          "anyOf": [
            {
              "$ref": "#/$defs/Modality"
            },
            {
              "type": "string"
            }
          ],
          "description": "The general modality of the data if it is known. Instrumentations SHOULD also set the mimeType field if the specific type is known.",
          "title": "Modality"
        },
        "content": {
          "description": "Raw bytes of the attached data. This field SHOULD be encoded as a base64 string when serialized to JSON.",
          "format": "binary",
          "title": "Content",
          "type": "string"
        }
      },
      "required": [
        "type",
        "modality",
        "content"
      ],
      "title": "BlobPart",
      "type": "object"
    },
    "ChatMessage": {
      "additionalProperties": true,
      "properties": {
        "role": {
          "anyOf": [
            {
              "$ref": "#/$defs/Role"
            },
            {
              "type": "string"
            }
          ],
          "description": "Role of the entity that created the message.",
          "title": "Role"
        },
        "parts": {
          "description": "List of message parts that make up the message content.",
          "items": {
            "anyOf": [
              {
                "$ref": "#/$defs/TextPart"
              },
              {
                "$ref": "#/$defs/ToolCallRequestPart"
              },
              {
                "$ref": "#/$defs/ToolCallResponsePart"
              },
              {
                "$ref": "#/$defs/ServerToolCallPart"
              },
              {
                "$ref": "#/$defs/ServerToolCallResponsePart"
              },
              {
                "$ref": "#/$defs/BlobPart"
              },
              {
                "$ref": "#/$defs/FilePart"
              },
              {
                "$ref": "#/$defs/UriPart"
              },
              {
                "$ref": "#/$defs/ReasoningPart"
              },
              {
                "$ref": "#/$defs/CompactionPart"
              },
              {
                "$ref": "#/$defs/GenericPart"
              }
            ]
          },
          "title": "Parts",
          "type": "array"
        },
        "name": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "The name of the participant.",
          "title": "Name"
        }
      },
      "required": [
        "role",
        "parts"
      ],
      "title": "ChatMessage",
      "type": "object"
    },
    "CompactionPart": {
      "additionalProperties": true,
      "description": "Represents compacted conversation state sent to or received from the model.",
      "properties": {
        "type": {
          "const": "compaction",
          "description": "The type of the content captured in this part.",
          "title": "Type",
          "type": "string"
        },
        "id": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Provider-assigned identifier for the compaction item or block.",
          "title": "Id"
        },
        "content": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "The unencrypted compacted conversation summary, when available.",
          "title": "Content"
        }
      },
      "required": [
        "type"
      ],
      "title": "CompactionPart",
      "type": "object"
    },
    "FilePart": {
      "additionalProperties": true,
      "description": "Represents an external referenced file sent to the model by file id",
      "properties": {
        "type": {
          "const": "file",
          "description": "The type of the content captured in this part.",
          "title": "Type",
          "type": "string"
        },
        "mime_type": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "The IANA MIME type of the attached data.",
          "title": "Mime Type"
        },
        "modality": {
          "anyOf": [
            {
              "$ref": "#/$defs/Modality"
            },
            {
              "type": "string"
            }
          ],
          "description": "The general modality of the data if it is known. Instrumentations SHOULD also set the mimeType field if the specific type is known.",
          "title": "Modality"
        },
        "file_id": {
          "description": "An identifier referencing a file that was pre-uploaded to the provider.",
          "title": "File Id",
          "type": "string"
        }
      },
      "required": [
        "type",
        "modality",
        "file_id"
      ],
      "title": "FilePart",
      "type": "object"
    },
    "GenericPart": {
      "additionalProperties": true,
      "description": "Represents an arbitrary message part with any type and properties.\nThis allows for extensibility with custom message part types.",
      "properties": {
        "type": {
          "description": "The type of the content captured in this part.",
          "title": "Type",
          "type": "string"
        }
      },
      "required": [
        "type"
      ],
      "title": "GenericPart",
      "type": "object"
    },
    "GenericServerToolCall": {
      "additionalProperties": true,
      "description": "Represents an arbitrary server tool call with any type and properties.\nThis allows for extensibility with custom server tool types.",
      "properties": {
        "type": {
          "description": "Type identifier for the server tool call.",
          "title": "Type",
          "type": "string"
        }
      },
      "required": [
        "type"
      ],
      "title": "GenericServerToolCall",
      "type": "object"
    },
    "GenericServerToolCallResponse": {
      "additionalProperties": true,
      "description": "Represents an arbitrary server tool call response with any type and properties.\nThis allows for extensibility with custom server tool response types.",
      "properties": {
        "type": {
          "description": "Type identifier for the server tool call response.",
          "title": "Type",
          "type": "string"
        }
      },
      "required": [
        "type"
      ],
      "title": "GenericServerToolCallResponse",
      "type": "object"
    },
    "Modality": {
      "enum": [
        "image",
        "video",
        "audio",
        "document"
      ],
      "title": "Modality",
      "type": "string"
    },
    "ReasoningPart": {
      "additionalProperties": true,
      "description": "Represents reasoning/thinking content received from the model.",
      "properties": {
        "type": {
          "const": "reasoning",
          "description": "The type of the content captured in this part.",
          "title": "Type",
          "type": "string"
        },
        "content": {
          "description": "Reasoning/thinking content received from the model.",
          "title": "Content",
          "type": "string"
        }
      },
      "required": [
        "type",
        "content"
      ],
      "title": "ReasoningPart",
      "type": "object"
    },
    "Role": {
      "enum": [
        "system",
        "user",
        "assistant",
        "tool"
      ],
      "title": "Role",
      "type": "string"
    },
    "ServerToolCallPart": {
      "additionalProperties": true,
      "description": "Represents a server-side tool call invocation. Server tool calls are executed by the model provider on the server side rather than by the client application. Provider-specific tools (e.g., code_interpreter, web_search) can have well-defined schemas defined by the respective providers.",
      "properties": {
        "type": {
          "const": "server_tool_call",
          "description": "The type of the content captured in this part.",
          "title": "Type",
          "type": "string"
        },
        "id": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Unique identifier for the server tool call.",
          "title": "Id"
        },
        "name": {
          "description": "Name of the server tool.",
          "title": "Name",
          "type": "string"
        },
        "server_tool_call": {
          "$ref": "#/$defs/GenericServerToolCall",
          "description": "Polymorphic server tool call details with type discriminator. The structure varies based on the tool type."
        }
      },
      "required": [
        "type",
        "name",
        "server_tool_call"
      ],
      "title": "ServerToolCallPart",
      "type": "object"
    },
    "ServerToolCallResponsePart": {
      "additionalProperties": true,
      "description": "Represents a server-side tool call response. Contains the outcome and details of a server tool execution. Provider-specific tools (e.g., code_interpreter, web_search) can have well-defined response schemas defined by the respective providers.",
      "properties": {
        "type": {
          "const": "server_tool_call_response",
          "description": "The type of the content captured in this part.",
          "title": "Type",
          "type": "string"
        },
        "id": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Unique server tool call identifier matching the original call.",
          "title": "Id"
        },
        "server_tool_call_response": {
          "$ref": "#/$defs/GenericServerToolCallResponse",
          "description": "Polymorphic server tool call response with type discriminator. The structure varies based on the tool type."
        }
      },
      "required": [
        "type",
        "server_tool_call_response"
      ],
      "title": "ServerToolCallResponsePart",
      "type": "object"
    },
    "TextPart": {
      "additionalProperties": true,
      "description": "Represents text content sent to or received from the model.",
      "properties": {
        "type": {
          "const": "text",
          "description": "The type of the content captured in this part.",
          "title": "Type",
          "type": "string"
        },
        "content": {
          "description": "Text content sent to or received from the model.",
          "title": "Content",
          "type": "string"
        }
      },
      "required": [
        "type",
        "content"
      ],
      "title": "TextPart",
      "type": "object"
    },
    "ToolCallRequestPart": {
      "additionalProperties": true,
      "description": "Represents a tool call requested by the model.",
      "properties": {
        "type": {
          "const": "tool_call",
          "description": "The type of the content captured in this part.",
          "title": "Type",
          "type": "string"
        },
        "id": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Unique identifier for the tool call.",
          "title": "Id"
        },
        "name": {
          "description": "Name of the tool.",
          "title": "Name",
          "type": "string"
        },
        "arguments": {
          "default": null,
          "description": "Arguments for the tool call.",
          "title": "Arguments"
        }
      },
      "required": [
        "type",
        "name"
      ],
      "title": "ToolCallRequestPart",
      "type": "object"
    },
    "ToolCallResponsePart": {
      "additionalProperties": true,
      "description": "Represents a tool call result sent to the model or a built-in tool call outcome and details.",
      "properties": {
        "type": {
          "const": "tool_call_response",
          "description": "The type of the content captured in this part.",
          "title": "Type",
          "type": "string"
        },
        "id": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Unique tool call identifier.",
          "title": "Id"
        },
        "response": {
          "description": "Tool call response.",
          "title": "Response"
        }
      },
      "required": [
        "type",
        "response"
      ],
      "title": "ToolCallResponsePart",
      "type": "object"
    },
    "UriPart": {
      "additionalProperties": true,
      "description": "Represents an external referenced file sent to the model by URI",
      "properties": {
        "type": {
          "const": "uri",
          "description": "The type of the content captured in this part.",
          "title": "Type",
          "type": "string"
        },
        "mime_type": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "The IANA MIME type of the attached data.",
          "title": "Mime Type"
        },
        "modality": {
          "anyOf": [
            {
              "$ref": "#/$defs/Modality"
            },
            {
              "type": "string"
            }
          ],
          "description": "The general modality of the data if it is known. Instrumentations SHOULD also set the mimeType field if the specific type is known.",
          "title": "Modality"
        },
        "uri": {
          "description": "A URI referencing attached data. It should not be a base64 data URL, which should use the `blob` part instead. The URI may use a scheme known to the provider api (e.g. `gs://bucket/object.png`), or be a publicly accessible location.",
          "title": "Uri",
          "type": "string"
        }
      },
      "required": [
        "type",
        "modality",
        "uri"
      ],
      "title": "UriPart",
      "type": "object"
    }
  },
  "description": "Represents the list of input messages sent to the model.",
  "items": {
    "$ref": "#/$defs/ChatMessage"
  },
  "title": "InputMessages",
  "type": "array"
}

_schema_output_messages := {
  "$defs": {
    "BlobPart": {
      "description": "Represents blob binary data sent inline to the model",
      "properties": {
        "type": {
          "const": "blob",
          "description": "The type of the content captured in this part.",
          "title": "Type",
          "type": "string"
        },
        "mime_type": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "The IANA MIME type of the attached data.",
          "title": "Mime Type"
        },
        "modality": {
          "anyOf": [
            {
              "$ref": "#/$defs/Modality"
            },
            {
              "type": "string"
            }
          ],
          "description": "The general modality of the data if it is known. Instrumentations SHOULD also set the mimeType field if the specific type is known.",
          "title": "Modality"
        },
        "content": {
          "description": "Raw bytes of the attached data. This field SHOULD be encoded as a base64 string when serialized to JSON.",
          "format": "binary",
          "title": "Content",
          "type": "string"
        }
      },
      "required": [
        "type",
        "modality",
        "content"
      ],
      "title": "BlobPart",
      "type": "object"
    },
    "CompactionPart": {
      "additionalProperties": true,
      "description": "Represents compacted conversation state sent to or received from the model.",
      "properties": {
        "type": {
          "const": "compaction",
          "description": "The type of the content captured in this part.",
          "title": "Type",
          "type": "string"
        },
        "id": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Provider-assigned identifier for the compaction item or block.",
          "title": "Id"
        },
        "content": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "The unencrypted compacted conversation summary, when available.",
          "title": "Content"
        }
      },
      "required": [
        "type"
      ],
      "title": "CompactionPart",
      "type": "object"
    },
    "FilePart": {
      "additionalProperties": true,
      "description": "Represents an external referenced file sent to the model by file id",
      "properties": {
        "type": {
          "const": "file",
          "description": "The type of the content captured in this part.",
          "title": "Type",
          "type": "string"
        },
        "mime_type": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "The IANA MIME type of the attached data.",
          "title": "Mime Type"
        },
        "modality": {
          "anyOf": [
            {
              "$ref": "#/$defs/Modality"
            },
            {
              "type": "string"
            }
          ],
          "description": "The general modality of the data if it is known. Instrumentations SHOULD also set the mimeType field if the specific type is known.",
          "title": "Modality"
        },
        "file_id": {
          "description": "An identifier referencing a file that was pre-uploaded to the provider.",
          "title": "File Id",
          "type": "string"
        }
      },
      "required": [
        "type",
        "modality",
        "file_id"
      ],
      "title": "FilePart",
      "type": "object"
    },
    "FinishReason": {
      "description": "Represents the reason for finishing the generation.",
      "enum": [
        "stop",
        "length",
        "content_filter",
        "tool_call",
        "compaction",
        "error"
      ],
      "title": "FinishReason",
      "type": "string"
    },
    "GenericPart": {
      "additionalProperties": true,
      "description": "Represents an arbitrary message part with any type and properties.\nThis allows for extensibility with custom message part types.",
      "properties": {
        "type": {
          "description": "The type of the content captured in this part.",
          "title": "Type",
          "type": "string"
        }
      },
      "required": [
        "type"
      ],
      "title": "GenericPart",
      "type": "object"
    },
    "GenericServerToolCall": {
      "additionalProperties": true,
      "description": "Represents an arbitrary server tool call with any type and properties.\nThis allows for extensibility with custom server tool types.",
      "properties": {
        "type": {
          "description": "Type identifier for the server tool call.",
          "title": "Type",
          "type": "string"
        }
      },
      "required": [
        "type"
      ],
      "title": "GenericServerToolCall",
      "type": "object"
    },
    "GenericServerToolCallResponse": {
      "additionalProperties": true,
      "description": "Represents an arbitrary server tool call response with any type and properties.\nThis allows for extensibility with custom server tool response types.",
      "properties": {
        "type": {
          "description": "Type identifier for the server tool call response.",
          "title": "Type",
          "type": "string"
        }
      },
      "required": [
        "type"
      ],
      "title": "GenericServerToolCallResponse",
      "type": "object"
    },
    "Modality": {
      "enum": [
        "image",
        "video",
        "audio",
        "document"
      ],
      "title": "Modality",
      "type": "string"
    },
    "OutputMessage": {
      "additionalProperties": true,
      "description": "Represents an output message generated by the model or agent. The output message captures\nspecific response (choice, candidate).",
      "properties": {
        "role": {
          "anyOf": [
            {
              "$ref": "#/$defs/Role"
            },
            {
              "type": "string"
            }
          ],
          "description": "Role of the entity that created the message.",
          "title": "Role"
        },
        "parts": {
          "description": "List of message parts that make up the message content.",
          "items": {
            "anyOf": [
              {
                "$ref": "#/$defs/TextPart"
              },
              {
                "$ref": "#/$defs/ToolCallRequestPart"
              },
              {
                "$ref": "#/$defs/ToolCallResponsePart"
              },
              {
                "$ref": "#/$defs/ServerToolCallPart"
              },
              {
                "$ref": "#/$defs/ServerToolCallResponsePart"
              },
              {
                "$ref": "#/$defs/BlobPart"
              },
              {
                "$ref": "#/$defs/FilePart"
              },
              {
                "$ref": "#/$defs/UriPart"
              },
              {
                "$ref": "#/$defs/ReasoningPart"
              },
              {
                "$ref": "#/$defs/CompactionPart"
              },
              {
                "$ref": "#/$defs/GenericPart"
              }
            ]
          },
          "title": "Parts",
          "type": "array"
        },
        "name": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "The name of the participant.",
          "title": "Name"
        },
        "finish_reason": {
          "anyOf": [
            {
              "$ref": "#/$defs/FinishReason"
            },
            {
              "type": "string"
            }
          ],
          "description": "Reason for finishing the generation.",
          "title": "Finish Reason"
        }
      },
      "required": [
        "role",
        "parts",
        "finish_reason"
      ],
      "title": "OutputMessage",
      "type": "object"
    },
    "ReasoningPart": {
      "additionalProperties": true,
      "description": "Represents reasoning/thinking content received from the model.",
      "properties": {
        "type": {
          "const": "reasoning",
          "description": "The type of the content captured in this part.",
          "title": "Type",
          "type": "string"
        },
        "content": {
          "description": "Reasoning/thinking content received from the model.",
          "title": "Content",
          "type": "string"
        }
      },
      "required": [
        "type",
        "content"
      ],
      "title": "ReasoningPart",
      "type": "object"
    },
    "Role": {
      "enum": [
        "system",
        "user",
        "assistant",
        "tool"
      ],
      "title": "Role",
      "type": "string"
    },
    "ServerToolCallPart": {
      "additionalProperties": true,
      "description": "Represents a server-side tool call invocation. Server tool calls are executed by the model provider on the server side rather than by the client application. Provider-specific tools (e.g., code_interpreter, web_search) can have well-defined schemas defined by the respective providers.",
      "properties": {
        "type": {
          "const": "server_tool_call",
          "description": "The type of the content captured in this part.",
          "title": "Type",
          "type": "string"
        },
        "id": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Unique identifier for the server tool call.",
          "title": "Id"
        },
        "name": {
          "description": "Name of the server tool.",
          "title": "Name",
          "type": "string"
        },
        "server_tool_call": {
          "$ref": "#/$defs/GenericServerToolCall",
          "description": "Polymorphic server tool call details with type discriminator. The structure varies based on the tool type."
        }
      },
      "required": [
        "type",
        "name",
        "server_tool_call"
      ],
      "title": "ServerToolCallPart",
      "type": "object"
    },
    "ServerToolCallResponsePart": {
      "additionalProperties": true,
      "description": "Represents a server-side tool call response. Contains the outcome and details of a server tool execution. Provider-specific tools (e.g., code_interpreter, web_search) can have well-defined response schemas defined by the respective providers.",
      "properties": {
        "type": {
          "const": "server_tool_call_response",
          "description": "The type of the content captured in this part.",
          "title": "Type",
          "type": "string"
        },
        "id": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Unique server tool call identifier matching the original call.",
          "title": "Id"
        },
        "server_tool_call_response": {
          "$ref": "#/$defs/GenericServerToolCallResponse",
          "description": "Polymorphic server tool call response with type discriminator. The structure varies based on the tool type."
        }
      },
      "required": [
        "type",
        "server_tool_call_response"
      ],
      "title": "ServerToolCallResponsePart",
      "type": "object"
    },
    "TextPart": {
      "additionalProperties": true,
      "description": "Represents text content sent to or received from the model.",
      "properties": {
        "type": {
          "const": "text",
          "description": "The type of the content captured in this part.",
          "title": "Type",
          "type": "string"
        },
        "content": {
          "description": "Text content sent to or received from the model.",
          "title": "Content",
          "type": "string"
        }
      },
      "required": [
        "type",
        "content"
      ],
      "title": "TextPart",
      "type": "object"
    },
    "ToolCallRequestPart": {
      "additionalProperties": true,
      "description": "Represents a tool call requested by the model.",
      "properties": {
        "type": {
          "const": "tool_call",
          "description": "The type of the content captured in this part.",
          "title": "Type",
          "type": "string"
        },
        "id": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Unique identifier for the tool call.",
          "title": "Id"
        },
        "name": {
          "description": "Name of the tool.",
          "title": "Name",
          "type": "string"
        },
        "arguments": {
          "default": null,
          "description": "Arguments for the tool call.",
          "title": "Arguments"
        }
      },
      "required": [
        "type",
        "name"
      ],
      "title": "ToolCallRequestPart",
      "type": "object"
    },
    "ToolCallResponsePart": {
      "additionalProperties": true,
      "description": "Represents a tool call result sent to the model or a built-in tool call outcome and details.",
      "properties": {
        "type": {
          "const": "tool_call_response",
          "description": "The type of the content captured in this part.",
          "title": "Type",
          "type": "string"
        },
        "id": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Unique tool call identifier.",
          "title": "Id"
        },
        "response": {
          "description": "Tool call response.",
          "title": "Response"
        }
      },
      "required": [
        "type",
        "response"
      ],
      "title": "ToolCallResponsePart",
      "type": "object"
    },
    "UriPart": {
      "additionalProperties": true,
      "description": "Represents an external referenced file sent to the model by URI",
      "properties": {
        "type": {
          "const": "uri",
          "description": "The type of the content captured in this part.",
          "title": "Type",
          "type": "string"
        },
        "mime_type": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "The IANA MIME type of the attached data.",
          "title": "Mime Type"
        },
        "modality": {
          "anyOf": [
            {
              "$ref": "#/$defs/Modality"
            },
            {
              "type": "string"
            }
          ],
          "description": "The general modality of the data if it is known. Instrumentations SHOULD also set the mimeType field if the specific type is known.",
          "title": "Modality"
        },
        "uri": {
          "description": "A URI referencing attached data. It should not be a base64 data URL, which should use the `blob` part instead. The URI may use a scheme known to the provider api (e.g. `gs://bucket/object.png`), or be a publicly accessible location.",
          "title": "Uri",
          "type": "string"
        }
      },
      "required": [
        "type",
        "modality",
        "uri"
      ],
      "title": "UriPart",
      "type": "object"
    }
  },
  "description": "Represents the list of output messages generated by the model or agent.",
  "items": {
    "$ref": "#/$defs/OutputMessage"
  },
  "title": "OutputMessages",
  "type": "array"
}

_schema_system_instructions := {
  "$defs": {
    "GenericPart": {
      "additionalProperties": true,
      "description": "Represents an arbitrary message part with any type and properties.\nThis allows for extensibility with custom message part types.",
      "properties": {
        "type": {
          "description": "The type of the content captured in this part.",
          "title": "Type",
          "type": "string"
        }
      },
      "required": [
        "type"
      ],
      "title": "GenericPart",
      "type": "object"
    },
    "TextPart": {
      "additionalProperties": true,
      "description": "Represents text content sent to or received from the model.",
      "properties": {
        "type": {
          "const": "text",
          "description": "The type of the content captured in this part.",
          "title": "Type",
          "type": "string"
        },
        "content": {
          "description": "Text content sent to or received from the model.",
          "title": "Content",
          "type": "string"
        }
      },
      "required": [
        "type",
        "content"
      ],
      "title": "TextPart",
      "type": "object"
    }
  },
  "description": "Represents the system instructions provided to the model.",
  "items": {
    "anyOf": [
      {
        "$ref": "#/$defs/TextPart"
      },
      {
        "$ref": "#/$defs/GenericPart"
      }
    ]
  },
  "title": "SystemInstructions",
  "type": "array"
}

_schema_tool_definitions := {
  "$defs": {
    "FunctionToolDefinition": {
      "additionalProperties": true,
      "description": "Represents a tool definition in the form of a function.",
      "properties": {
        "type": {
          "const": "function",
          "description": "The type of the tool.",
          "title": "Type",
          "type": "string"
        },
        "name": {
          "description": "The name of the tool.",
          "title": "Name",
          "type": "string"
        },
        "description": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "The description of the tool. Since this attribute could be large, it's NOT RECOMMENDED to be populated by default. Instrumentations MAY provide a way to enable populating this property.",
          "title": "Description"
        },
        "parameters": {
          "anyOf": [
            {
              "type": "object"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "JSON Schema document describing the parameters accepted by the tool. The value MUST conform to JSON Schema draft-07. Since this attribute could be large, it's NOT RECOMMENDED to be populated by default. Instrumentations MAY provide a way to enable populating this property.",
          "title": "Parameters"
        }
      },
      "required": [
        "type",
        "name"
      ],
      "title": "FunctionToolDefinition",
      "type": "object"
    },
    "GenericToolDefinition": {
      "additionalProperties": true,
      "description": "Represents a tool definition in any form.",
      "properties": {
        "type": {
          "description": "The type of the tool.",
          "title": "Type",
          "type": "string"
        },
        "name": {
          "description": "The name of the tool.",
          "title": "Name",
          "type": "string"
        }
      },
      "required": [
        "type",
        "name"
      ],
      "title": "GenericToolDefinition",
      "type": "object"
    }
  },
  "description": "Represents the list of tool definitions available to the GenAI agent or model.",
  "items": {
    "anyOf": [
      {
        "$ref": "#/$defs/FunctionToolDefinition"
      },
      {
        "$ref": "#/$defs/GenericToolDefinition"
      }
    ]
  },
  "title": "ToolDefinitions",
  "type": "array"
}

_schema_retrieval_documents := {
  "$defs": {
    "RetrievalDocument": {
      "additionalProperties": true,
      "description": "Represents a single document retrieved from a vector database or search system.",
      "properties": {
        "id": {
          "description": "A unique identifier for the document.",
          "title": "Id",
          "type": "string"
        },
        "score": {
          "description": "The relevance score of the document.",
          "title": "Score",
          "type": "number"
        }
      },
      "required": [
        "id",
        "score"
      ],
      "title": "RetrievalDocument",
      "type": "object"
    }
  },
  "description": "Represents the list of documents retrieved from a vector database or search system.",
  "items": {
    "$ref": "#/$defs/RetrievalDocument"
  },
  "title": "RetrievalDocuments",
  "type": "array"
}
