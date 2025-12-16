# CITYARRAY Sovereign SDK

**Architecture Specification for Sovereign AI Deployment**

Version: 1.0  
Date: December 2024  
Classification: Strategic Planning

---

## 1. Overview

### 1.1 Purpose

The CITYARRAY Sovereign SDK enables municipal customers to deploy AI-powered emergency communication systems with **complete data sovereignty**. All data—video feeds, detection events, alert history, audit logs, and model weights—remains within the customer's jurisdiction and control.

### 1.2 Design Philosophy: Sovereign-First

Unlike traditional cloud-first architectures that treat on-premise as a degraded mode, the Sovereign SDK inverts this relationship:

```
TRADITIONAL APPROACH:
  Cloud-first → On-premise as "enterprise option" → Air-gapped as "special case"

SOVEREIGN-FIRST APPROACH:
  Air-gapped as default → On-premise as "connected option" → Cloud as "managed service add-on"
```

**Core Principle:** The system must function with zero external connectivity. Any cloud integration is additive, not required.

### 1.3 Target Deployments

| Deployment Type | Connectivity | Key Custody | Target Customer |
|-----------------|--------------|-------------|-----------------|
| Air-Gapped | None (data diode for IPAWS) | City-only or Federated | Critical infrastructure, military, high-security venues |
| On-Premise | Government networks only | Federated | Large cities, counties, state agencies |
| Hybrid | Selective cloud services | Federated or Split | Mid-size cities |
| Managed | Full cloud connectivity | OEM or Split | Small municipalities, private venues |

---

## 2. Architecture Principles

### 2.1 Data Never Leaves by Default

All data remains local unless explicitly configured otherwise:

- **Video streams**: Processed on-device, never transmitted
- **Detection events**: Stored locally, optional secure sync
- **Alert history**: Local database with tamper-evident logging
- **Audit logs**: Local with hash-chain integrity
- **Model weights**: Stored locally, updated via signed physical media

### 2.2 Offline-First Operation

Every component must function without network connectivity:

```
┌─────────────────────────────────────────────────────────────────┐
│                    SOVEREIGN DEPLOYMENT                         │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                 CITY DATA CENTER                          │  │
│  │                                                           │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐   │  │
│  │  │ CITYARRAY   │  │   City      │  │   Operator      │   │  │
│  │  │ Server      │  │   HSM       │  │   Dashboard     │   │  │
│  │  │             │  │             │  │                 │   │  │
│  │  └──────┬──────┘  └──────┬──────┘  └────────┬────────┘   │  │
│  │         │                │                   │            │  │
│  │         └────────────────┴───────────────────┘            │  │
│  │                          │                                │  │
│  │              City Network (Isolated)                      │  │
│  │                          │                                │  │
│  └──────────────────────────┼────────────────────────────────┘  │
│                             │                                   │
│  ┌──────────────────────────┼────────────────────────────────┐  │
│  │         EDGE DEVICES (Field Deployed)                     │  │
│  │                          │                                │  │
│  │    ┌─────────┐    ┌─────────┐    ┌─────────┐             │  │
│  │    │ Sign A  │    │ Sign B  │    │ Sign C  │   ...       │  │
│  │    │ Camera  │    │ Camera  │    │ Camera  │             │  │
│  │    │ AI Det. │    │ AI Det. │    │ AI Det. │             │  │
│  │    │ Display │    │ Display │    │ Display │             │  │
│  │    └─────────┘    └─────────┘    └─────────┘             │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ════════════════════════════════════════════════════════════   │
│                     AIR GAP BOUNDARY                            │
│  ════════════════════════════════════════════════════════════   │
│                             │                                   │
│                             │ One-Way Only (Data Diode)         │
│                             ▼                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    EXTERNAL SYSTEMS                        │  │
│  │                                                            │  │
│  │   ┌────────────┐    ┌────────────┐    ┌────────────┐      │  │
│  │   │   IPAWS    │    │  FirstNet  │    │ Neighbor   │      │  │
│  │   │   (FEMA)   │    │ (Optional) │    │ Jurisdict. │      │  │
│  │   └────────────┘    └────────────┘    └────────────┘      │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 Federated Key Custody

Different signing keys for different alert tiers:

| Tier | Key Location | Authorization Required | Rationale |
|------|--------------|------------------------|-----------|
| INFORMATIONAL | City HSM | None (autonomous) | Crowd counts, weather—no risk |
| ADVISORY | City HSM | None (autonomous) | Low-risk advisories |
| WARNING | City HSM | 1 city operator | Human-in-the-loop |
| EMERGENCY | City HSM | 2 city operators (M-of-N) | Multi-party prevents insider abuse |
| IPAWS | Federal (pass-through) | Pre-authorized by FEMA | City cannot modify federal alerts |

### 2.4 Defense in Depth

Security controls at every layer:

```
Layer 1: Physical Security
  └── Tamper-evident enclosures, locked facilities, access logs

Layer 2: Network Isolation
  └── Air gap, data diodes, network segmentation

Layer 3: Cryptographic Enforcement
  └── All messages signed, HSM-protected keys, certificate pinning

Layer 4: Multi-Party Authorization
  └── Critical alerts require multiple approvers

Layer 5: Audit Trail
  └── Hash-chained logs, tamper detection, 7-year retention
```

---

## 3. Component Architecture

### 3.1 Sovereign Server

The central server deployed in customer's data center.

```
cityarray-sovereign-server/
├── core/
│   ├── alert_queue.py          # Pending alert management
│   ├── authorization.py        # Multi-party approval workflow
│   ├── message_signing.py      # HSM integration for signing
│   └── device_registry.py      # Edge device management
├── security/
│   ├── hsm_interface.py        # Abstract HSM interface
│   ├── hsm_drivers/
│   │   ├── thales_luna.py      # Thales Luna HSM
│   │   ├── yubihsm.py          # YubiHSM (lower cost)
│   │   ├── aws_cloudhsm.py     # For hybrid deployments
│   │   └── software_hsm.py     # Development/testing only
│   ├── key_ceremony.py         # Key generation procedures
│   └── audit_logger.py         # Tamper-evident logging
├── integration/
│   ├── ipaws_receiver.py       # CAP alert ingestion
│   ├── data_diode.py           # One-way communication handler
│   ├── firstnet_bridge.py      # Government network integration
│   └── mutual_aid.py           # Cross-jurisdiction coordination
├── dashboard/
│   ├── operator_ui/            # Web-based operator interface
│   ├── admin_ui/               # System administration
│   └── audit_viewer/           # Log review and export
├── storage/
│   ├── alert_history.py        # Historical alert database
│   ├── detection_store.py      # Detection event archive
│   └── backup_manager.py       # Encrypted backup handling
└── api/
    ├── edge_api.py             # API for edge devices
    ├── operator_api.py         # API for dashboard
    └── integration_api.py      # API for external systems
```

### 3.2 Sovereign Edge SDK

Deployed on each edge device (LED sign with AI detection).

```
cityarray-sovereign-edge/
├── core/
│   ├── sdk.py                  # Main SDK orchestration
│   ├── config.py               # Device configuration
│   └── state_machine.py        # Operational states
├── detection/
│   ├── engine.py               # Detection orchestration
│   ├── yolo_detector.py        # YOLOv8 inference
│   ├── model_manager.py        # Model loading/validation
│   └── local_training.py       # Fine-tuning support
├── decision/
│   ├── classifier.py           # Alert tier classification
│   ├── rules_engine.py         # Configurable decision rules
│   └── templates.py            # Pre-approved message templates
├── display/
│   ├── secure_engine.py        # Signature-verified display
│   ├── led_driver.py           # Hardware abstraction
│   └── renderer.py             # Content rendering
├── security/
│   ├── message_verifier.py     # Signature verification
│   ├── device_identity.py      # Device certificate management
│   ├── secure_boot.py          # Boot integrity verification
│   └── audit_logger.py         # Local audit logging
├── communication/
│   ├── server_link.py          # Connection to sovereign server
│   ├── offline_queue.py        # Offline message queuing
│   └── sync_manager.py         # State synchronization
├── tts/
│   ├── engine.py               # Text-to-speech orchestration
│   ├── voices/                 # Offline voice models
│   └── multilingual.py         # Language support
└── sensors/
    ├── camera.py               # Camera interface
    ├── environmental.py        # Temperature, humidity, etc.
    └── tamper_detect.py        # Physical tamper detection
```

### 3.3 Component Interactions

```
┌─────────────────────────────────────────────────────────────────┐
│                      SOVEREIGN SERVER                           │
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐ │
│  │ Alert Queue │◄───│ IPAWS       │◄───│ Data Diode          │ │
│  │             │    │ Receiver    │    │ (One-Way In)        │ │
│  └──────┬──────┘    └─────────────┘    └─────────────────────┘ │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────┐    ┌─────────────┐                            │
│  │Authorization│───►│   HSM       │                            │
│  │  Workflow   │    │  Signing    │                            │
│  └──────┬──────┘    └──────┬──────┘                            │
│         │                  │                                    │
│         ▼                  ▼                                    │
│  ┌─────────────────────────────────┐    ┌─────────────────────┐│
│  │      Signed Message Queue       │    │    Audit Logger     ││
│  └──────────────┬──────────────────┘    └─────────────────────┘│
│                 │                                               │
└─────────────────┼───────────────────────────────────────────────┘
                  │
                  │ City Network (Isolated)
                  │
┌─────────────────┼───────────────────────────────────────────────┐
│                 ▼           EDGE DEVICE                         │
│  ┌─────────────────────────────────┐                           │
│  │      Message Verifier           │ ◄─── Reject if invalid    │
│  └──────────────┬──────────────────┘                           │
│                 │                                               │
│                 ▼                                               │
│  ┌─────────────────────────────────┐                           │
│  │      Secure Display Engine      │                           │
│  └──────────────┬──────────────────┘                           │
│                 │                                               │
│                 ▼                                               │
│  ┌─────────────────────────────────┐                           │
│  │         LED Matrix              │                           │
│  └─────────────────────────────────┘                           │
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐ │
│  │   Camera    │───►│  Detection  │───►│  Decision Engine    │ │
│  │             │    │  (YOLOv8)   │    │  (Tier Assignment)  │ │
│  └─────────────┘    └─────────────┘    └──────────┬──────────┘ │
│                                                   │             │
│                                                   ▼             │
│                                        ┌─────────────────────┐  │
│                                        │ Detection Event     │  │
│                                        │ (Sent to Server)    │  │
│                                        └─────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Security Architecture

### 4.1 Key Hierarchy

```
Root CA Key (Offline, Air-Gapped)
│
├── Sovereign Server CA (City HSM)
│   │
│   ├── Message Signing Key (per tier)
│   │   ├── informational_signing_key
│   │   ├── advisory_signing_key
│   │   ├── warning_signing_key
│   │   └── emergency_signing_key
│   │
│   └── Device Certificate Issuing Key
│       └── Per-device identity certificates
│
└── IPAWS Trust Anchor (Federal, Read-Only)
    └── Verify federal alert signatures (cannot sign)
```

### 4.2 Message Signing Flow

```python
# Server-side signing (simplified)
class SovereignMessageSigner:
    def sign_message(
        self,
        content: dict,
        tier: AlertTier,
        target_devices: list[str],
        authorizations: list[Authorization]
    ) -> SignedMessage:
        
        # 1. Validate authorization requirements
        if not self.validate_authorizations(tier, authorizations):
            raise InsufficientAuthorizationError(
                f"Tier {tier} requires {tier.min_authorizations} authorizations"
            )
        
        # 2. Select appropriate signing key for tier
        signing_key_id = self.get_signing_key_for_tier(tier)
        
        # 3. Build message payload
        message = SignedMessage(
            message_id=generate_uuid(),
            tier=tier,
            content=content,
            target_devices=target_devices,
            timestamp=utc_now(),
            expires=utc_now() + tier.ttl,
            nonce=generate_nonce(),
            authorizations=authorizations
        )
        
        # 4. Sign using HSM (key never leaves HSM)
        signature = self.hsm.sign(
            key_id=signing_key_id,
            data=message.canonical_bytes()
        )
        
        message.signature = signature
        
        # 5. Log to audit trail
        self.audit.log_message_signed(message, authorizations)
        
        return message
```

### 4.3 Edge Verification Flow

```python
# Edge-side verification (simplified)
class SovereignMessageVerifier:
    def verify_and_display(self, message: SignedMessage) -> bool:
        
        # 1. Check message is for this device
        if self.device_id not in message.target_devices:
            if "*" not in message.target_devices:  # Broadcast
                self.audit.log_rejected(message, "wrong_device")
                return False
        
        # 2. Check not expired
        if message.is_expired():
            self.audit.log_rejected(message, "expired")
            return False
        
        # 3. Check not replay
        if self.nonce_cache.seen(message.nonce):
            self.audit.log_rejected(message, "replay_detected")
            return False
        
        # 4. Get public key for this tier
        public_key = self.get_public_key_for_tier(message.tier)
        
        # 5. Verify signature
        if not self.verify_signature(message, public_key):
            self.audit.log_rejected(message, "invalid_signature")
            self.alert_tamper_detected()
            return False
        
        # 6. Record nonce to prevent replay
        self.nonce_cache.record(message.nonce)
        
        # 7. Display message
        self.display_engine.render(message.content)
        
        # 8. Log successful display
        self.audit.log_displayed(message)
        
        return True
```

### 4.4 HSM Interface

Abstract interface supporting multiple HSM vendors:

```python
from abc import ABC, abstractmethod

class HSMInterface(ABC):
    """
    Abstract HSM interface for sovereign deployments.
    
    Supported implementations:
    - ThalesLunaHSM: Enterprise-grade, FIPS 140-2 Level 3
    - YubiHSM: Lower cost, FIPS 140-2 Level 3
    - SoftwareHSM: Development/testing only (NOT FOR PRODUCTION)
    """
    
    @abstractmethod
    def generate_key(
        self,
        key_id: str,
        algorithm: str = "ed25519",
        extractable: bool = False
    ) -> KeyInfo:
        """Generate a new signing key. Key never leaves HSM."""
        pass
    
    @abstractmethod
    def sign(self, key_id: str, data: bytes) -> bytes:
        """Sign data using key in HSM. Key material never exposed."""
        pass
    
    @abstractmethod
    def get_public_key(self, key_id: str) -> bytes:
        """Export public key (safe to distribute)."""
        pass
    
    @abstractmethod
    def destroy_key(self, key_id: str, authorization: MultiPartyAuth) -> bool:
        """Destroy key. Requires multi-party authorization."""
        pass
    
    @abstractmethod
    def audit_log(self) -> list[HSMOperation]:
        """Get HSM operation audit log."""
        pass
```

---

## 5. IPAWS Integration

### 5.1 Data Diode Architecture

```
┌────────────────────┐         ┌────────────────────┐
│   IPAWS OPEN       │         │   SOVEREIGN        │
│   (Internet)       │         │   NETWORK          │
│                    │         │                    │
│  ┌──────────────┐  │         │  ┌──────────────┐  │
│  │ CAP Alert    │  │ ──────► │  │ Diode        │  │
│  │ Feed         │  │  FIBER  │  │ Receiver     │  │
│  └──────────────┘  │  (TX)   │  └──────┬───────┘  │
│                    │         │         │          │
│  ┌──────────────┐  │         │         │          │
│  │ NO DATA      │◄─┼─── X ───┼─────────┘          │
│  │ (Blocked)    │  │         │  (No return path)  │
│  └──────────────┘  │         │                    │
└────────────────────┘         └────────────────────┘
        │                               │
        │                               │
   Physically                    Physically
   impossible                    impossible
   to receive                    to transmit
   from sovereign                to internet
```

### 5.2 CAP Message Handling

```python
class IPAWSReceiver:
    """
    Receives IPAWS alerts via data diode.
    
    IPAWS alerts are pre-signed by federal authority.
    City cannot modify content—display as pass-through.
    """
    
    def __init__(self, diode_interface: DataDiodeInterface):
        self.diode = diode_interface
        self.cap_parser = CAPParser()
        self.federal_trust_anchor = load_federal_public_keys()
    
    def process_incoming(self, raw_data: bytes) -> Optional[IPAWSAlert]:
        # 1. Parse CAP message
        try:
            cap_message = self.cap_parser.parse(raw_data)
        except CAPParseError as e:
            self.audit.log_ipaws_parse_error(e)
            return None
        
        # 2. Verify federal signature
        if not self.verify_federal_signature(cap_message):
            self.audit.log_ipaws_signature_invalid(cap_message)
            return None
        
        # 3. Check geographic relevance
        if not self.is_relevant_to_jurisdiction(cap_message):
            self.audit.log_ipaws_out_of_area(cap_message)
            return None
        
        # 4. Convert to internal format (preserve federal signature)
        alert = IPAWSAlert(
            original_cap=cap_message,
            federal_signature=cap_message.signature,
            received_at=utc_now(),
            tier=AlertTier.IPAWS  # Special tier, no local signing needed
        )
        
        # 5. Queue for immediate display
        self.alert_queue.enqueue_priority(alert)
        
        self.audit.log_ipaws_received(alert)
        return alert
    
    def verify_federal_signature(self, cap_message: CAPMessage) -> bool:
        """Verify using federal trust anchor. Cannot forge."""
        for public_key in self.federal_trust_anchor:
            if cap_message.verify_signature(public_key):
                return True
        return False
```

### 5.3 Supported Data Diode Vendors

| Vendor | Model | Throughput | Certification | Estimated Cost |
|--------|-------|------------|---------------|----------------|
| Owl Cyber Defense | DualDiode | 1 Gbps | NSA CSfC | $25,000 - $50,000 |
| Waterfall Security | FLIP | 100 Mbps | ICS-CERT | $15,000 - $30,000 |
| Fox-IT | DataDiode | 1 Gbps | NATO | $30,000 - $60,000 |
| Advenica | SecuriCDS | 10 Gbps | EU certified | $40,000 - $80,000 |

---

## 6. Cross-Jurisdiction Coordination

### 6.1 Mutual Aid Protocol

When an emergency spans multiple jurisdictions:

```
┌─────────────────┐              ┌─────────────────┐
│   CITY A        │              │   CITY B        │
│   Sovereign     │              │   Sovereign     │
│   Deployment    │              │   Deployment    │
│                 │              │                 │
│  ┌───────────┐  │   FirstNet   │  ┌───────────┐  │
│  │ Mutual Aid│  │◄────────────►│  │ Mutual Aid│  │
│  │ Gateway   │  │   or Fiber   │  │ Gateway   │  │
│  └───────────┘  │              │  └───────────┘  │
│                 │              │                 │
│  City A HSM     │              │  City B HSM     │
│  signs for      │              │  signs for      │
│  City A only    │              │  City B only    │
└─────────────────┘              └─────────────────┘
```

### 6.2 Alert Relay Process

```python
class MutualAidGateway:
    """
    Handles cross-jurisdiction alert coordination.
    
    Each city maintains sovereignty—incoming alerts are
    re-signed by local HSM before display.
    """
    
    def __init__(
        self,
        local_signer: SovereignMessageSigner,
        trusted_peers: dict[str, PeerJurisdiction]
    ):
        self.signer = local_signer
        self.peers = trusted_peers
    
    def receive_peer_alert(
        self,
        alert: MutualAidAlert,
        source_jurisdiction: str
    ) -> bool:
        # 1. Verify source is trusted peer
        if source_jurisdiction not in self.peers:
            self.audit.log_untrusted_peer(source_jurisdiction)
            return False
        
        peer = self.peers[source_jurisdiction]
        
        # 2. Verify peer's signature
        if not alert.verify_signature(peer.public_key):
            self.audit.log_peer_signature_invalid(alert, peer)
            return False
        
        # 3. Check mutual aid agreement allows this alert type
        if not peer.agreement.allows_alert_type(alert.type):
            self.audit.log_agreement_violation(alert, peer)
            return False
        
        # 4. RE-SIGN with local HSM (sovereignty preserved)
        #    Original alert becomes "supporting evidence"
        local_alert = self.signer.sign_message(
            content=alert.content,
            tier=alert.tier,
            target_devices=self.get_relevant_devices(alert),
            authorizations=[
                Authorization(
                    type="mutual_aid",
                    source_jurisdiction=source_jurisdiction,
                    original_signature=alert.signature
                )
            ]
        )
        
        # 5. Queue for local authorization workflow
        #    (Still requires local operator confirmation for WARNING+)
        self.alert_queue.enqueue(local_alert)
        
        return True
```

### 6.3 Network Options

| Network | Security | Availability | Best For |
|---------|----------|--------------|----------|
| FirstNet (LTE) | High (dedicated spectrum) | Good | Most jurisdictions |
| State Emergency Network | High | Varies | State agencies |
| Dedicated Fiber | Maximum | Excellent | Adjacent cities |
| LoRa Mesh | Medium | Works when internet down | Disaster resilience |
| P25 Radio | High | Works when everything down | Last resort |

---

## 7. Local Model Fine-Tuning

### 7.1 Training Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    LOCAL TRAINING ENVIRONMENT                   │
│                    (Isolated from Production)                   │
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │ Training Data   │    │ Base Model      │                    │
│  │ (Local cameras) │    │ (OEM provided)  │                    │
│  └────────┬────────┘    └────────┬────────┘                    │
│           │                      │                              │
│           ▼                      ▼                              │
│  ┌─────────────────────────────────────────┐                   │
│  │           Fine-Tuning Pipeline          │                   │
│  │                                         │                   │
│  │  1. Data augmentation                   │                   │
│  │  2. Transfer learning                   │                   │
│  │  3. Local validation                    │                   │
│  └────────────────────┬────────────────────┘                   │
│                       │                                         │
│                       ▼                                         │
│  ┌─────────────────────────────────────────┐                   │
│  │         OEM Validation Suite            │                   │
│  │                                         │                   │
│  │  • Accuracy benchmarks (must pass)      │                   │
│  │  • Adversarial robustness tests         │                   │
│  │  • False positive rate limits           │                   │
│  │  • Performance regression checks        │                   │
│  └────────────────────┬────────────────────┘                   │
│                       │                                         │
│              ┌────────┴────────┐                                │
│              │                 │                                │
│           PASS              FAIL                                │
│              │                 │                                │
│              ▼                 ▼                                │
│  ┌───────────────────┐  ┌───────────────────┐                  │
│  │ Deploy to Prod    │  │ Return to         │                  │
│  │ (City signs off)  │  │ Training          │                  │
│  └───────────────────┘  └───────────────────┘                  │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 Model Manager

```python
class LocalModelManager:
    """
    Manages detection models including local fine-tuning.
    
    Training data NEVER leaves city network.
    Fine-tuned models are city property.
    """
    
    def __init__(
        self,
        base_model_path: Path,
        validation_suite: OEMValidationSuite
    ):
        self.base_model = self.load_model(base_model_path)
        self.validation = validation_suite
        self.active_model = self.base_model
    
    def fine_tune(
        self,
        training_data: LocalDataset,
        config: FineTuneConfig
    ) -> FineTuneResult:
        """
        Fine-tune model on local data.
        
        Data never leaves city network.
        Resulting model owned by city.
        """
        # 1. Validate training data quality
        data_quality = self.assess_data_quality(training_data)
        if data_quality.score < config.min_quality:
            return FineTuneResult(
                success=False,
                reason=f"Data quality {data_quality.score} below threshold"
            )
        
        # 2. Fine-tune in isolated environment
        fine_tuned = self.trainer.fine_tune(
            base=self.base_model,
            data=training_data,
            config=config
        )
        
        # 3. Run OEM validation suite
        validation_result = self.validation.validate(fine_tuned)
        
        if not validation_result.passed:
            return FineTuneResult(
                success=False,
                reason=f"Validation failed: {validation_result.failures}"
            )
        
        # 4. Generate model certificate (city signs)
        certificate = ModelCertificate(
            model_hash=fine_tuned.hash(),
            base_model_version=self.base_model.version,
            training_data_hash=training_data.hash(),
            validation_results=validation_result,
            certified_by="city",  # City accepts responsibility
            timestamp=utc_now()
        )
        
        return FineTuneResult(
            success=True,
            model=fine_tuned,
            certificate=certificate
        )
    
    def deploy_model(
        self,
        model: FineTunedModel,
        certificate: ModelCertificate,
        authorization: MultiPartyAuth
    ) -> bool:
        """
        Deploy fine-tuned model to production.
        
        Requires multi-party authorization (city accepts liability).
        """
        # Verify certificate
        if not certificate.verify():
            return False
        
        # Verify authorization
        if not authorization.verify(required_parties=2):
            return False
        
        # Deploy
        self.active_model = model
        self.audit.log_model_deployed(model, certificate, authorization)
        
        return True
```

### 7.3 Dual-Model Safety Option

For high-risk deployments, run both base and fine-tuned models:

```python
class DualModelDetector:
    """
    Runs both base and fine-tuned models.
    
    For WARNING/EMERGENCY tiers, both models must agree.
    Prevents fine-tuning errors from causing false alerts.
    """
    
    def __init__(self, base_model: Model, fine_tuned_model: Model):
        self.base = base_model
        self.fine_tuned = fine_tuned_model
    
    def detect(self, frame: np.ndarray) -> list[Detection]:
        base_detections = self.base.detect(frame)
        tuned_detections = self.fine_tuned.detect(frame)
        
        # For INFO/ADVISORY: Use fine-tuned (better local accuracy)
        # For WARNING/EMERGENCY: Require agreement
        
        return self.merge_detections(base_detections, tuned_detections)
    
    def merge_detections(
        self,
        base: list[Detection],
        tuned: list[Detection]
    ) -> list[Detection]:
        results = []
        
        for detection in tuned:
            tier = get_tier_for_detection(detection)
            
            if tier in (AlertTier.INFORMATIONAL, AlertTier.ADVISORY):
                # Trust fine-tuned model
                results.append(detection)
            else:
                # Require base model agreement for high-risk tiers
                if self.has_matching_detection(detection, base):
                    results.append(detection)
                else:
                    self.audit.log_detection_disagreement(detection, base)
        
        return results
```

---

## 8. Update Management

### 8.1 Air-Gapped Update Process

```
┌─────────────────────────────────────────────────────────────────┐
│                    UPDATE CEREMONY                              │
│                                                                 │
│  Step 1: OEM prepares update package                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ • Software update (signed by OEM)                        │   │
│  │ • Release notes                                          │   │
│  │ • Validation checksums                                   │   │
│  │ • OEM signature                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│                           ▼                                     │
│  Step 2: Transfer to secure USB (OEM facility)                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ • Write-once media preferred                             │   │
│  │ • Tamper-evident packaging                               │   │
│  │ • Chain of custody documentation                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│                           ▼                                     │
│  Step 3: Physical delivery to city                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ • Bonded courier or city pickup                          │   │
│  │ • Verify tamper-evident seals                            │   │
│  │ • Log receipt in chain of custody                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│                           ▼                                     │
│  Step 4: City verification (isolated system)                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ • Verify OEM signature                                   │   │
│  │ • Verify checksums                                       │   │
│  │ • Scan for malware (city tools)                          │   │
│  │ • Test in staging environment                            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│                           ▼                                     │
│  Step 5: Multi-party authorization                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ • Minimum 2 city personnel authorize                     │   │
│  │ • Log authorization in audit trail                       │   │
│  │ • Schedule maintenance window                            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│                           ▼                                     │
│  Step 6: Apply update                                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ • Staged rollout (test devices first)                    │   │
│  │ • Automatic rollback if validation fails                 │   │
│  │ • Full audit logging                                     │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 8.2 Update Package Structure

```
cityarray-update-2024.12.001/
├── manifest.json              # Package contents, versions
├── signatures/
│   ├── oem_signature.sig      # OEM signs entire package
│   └── checksums.sha256       # File-level checksums
├── server/
│   ├── cityarray-server-2.1.0.tar.gz
│   └── migrations/            # Database migrations
├── edge/
│   ├── cityarray-edge-2.1.0.tar.gz
│   └── firmware/              # Device firmware updates
├── models/
│   ├── yolov8n-cityarray-2.1.0.onnx
│   └── model_certificate.json
├── docs/
│   ├── RELEASE_NOTES.md
│   ├── CHANGELOG.md
│   └── UPGRADE_GUIDE.md
└── validation/
    ├── test_suite.py          # Automated validation tests
    └── expected_results.json
```

---

## 9. Audit & Compliance

### 9.1 Audit Log Schema

```python
@dataclass
class AuditEntry:
    # Identity
    sequence: int              # Monotonic sequence number
    entry_id: str              # UUID
    
    # Timestamp
    timestamp: datetime        # UTC
    
    # Chain integrity
    previous_hash: str         # SHA-256 of previous entry
    entry_hash: str            # SHA-256 of this entry
    
    # Event details
    event_type: AuditEventType
    severity: AuditSeverity    # INFO, WARNING, CRITICAL
    
    # Actor
    actor_type: str            # system, operator, device, external
    actor_id: str              # Who/what performed action
    
    # Action
    action: str                # What was done
    target: str                # What it was done to
    
    # Context
    device_id: Optional[str]
    session_id: Optional[str]
    ip_address: Optional[str]
    
    # Outcome
    success: bool
    error_message: Optional[str]
    
    # Evidence
    details: dict              # Action-specific details
    attachments: list[str]     # Hashes of related artifacts
```

### 9.2 Retention Requirements

| Event Category | Retention Period | Storage Location | Rationale |
|----------------|------------------|------------------|-----------|
| Alert Display | 7 years | Immutable storage | Legal liability |
| Authorization | 7 years | Immutable storage | Chain of custody |
| Security Events | 7 years | Immutable storage | Incident investigation |
| Detection Events | 90 days | Standard storage | Operational tuning |
| System Events | 1 year | Standard storage | Troubleshooting |
| Video Footage | Per city policy | City-managed | Privacy regulations |

### 9.3 Compliance Frameworks

The Sovereign SDK supports compliance with:

- **CJIS** (Criminal Justice Information Services) — for law enforcement integration
- **FedRAMP** — for federal facility deployments (hybrid mode)
- **StateRAMP** — for state agency deployments
- **SOC 2 Type II** — for managed service offerings
- **GDPR** — for international deployments (data never leaves jurisdiction)

---

## 10. Implementation Phases

### Phase 1: Core Sovereign Infrastructure (Months 1-3)

- [ ] Sovereign Server core (alert queue, authorization workflow)
- [ ] HSM integration (Thales Luna, YubiHSM drivers)
- [ ] Federated key management
- [ ] Edge signature verification
- [ ] Tamper-evident audit logging
- [ ] Basic operator dashboard

### Phase 2: IPAWS Integration (Months 3-4)

- [ ] CAP message parser
- [ ] Data diode interface
- [ ] Federal signature verification
- [ ] IPAWS alert rendering
- [ ] Geographic filtering

### Phase 3: Cross-Jurisdiction (Months 4-6)

- [ ] Mutual aid protocol
- [ ] FirstNet integration
- [ ] Peer trust management
- [ ] Alert relay and re-signing
- [ ] Multi-jurisdiction dashboard

### Phase 4: Local AI (Months 6-8)

- [ ] Fine-tuning pipeline
- [ ] Validation suite
- [ ] Dual-model safety option
- [ ] Model certification workflow
- [ ] Training data management

### Phase 5: Hardening (Months 8-10)

- [ ] Third-party penetration testing
- [ ] Compliance documentation
- [ ] Disaster recovery procedures
- [ ] Key ceremony documentation
- [ ] Operational runbooks

### Phase 6: Certification (Months 10-12)

- [ ] SOC 2 Type II audit
- [ ] StateRAMP assessment (if applicable)
- [ ] Customer pilot deployments
- [ ] Documentation finalization

---

## 11. Appendices

### A. Glossary

| Term | Definition |
|------|------------|
| Air Gap | Physical network isolation with no bidirectional connectivity |
| CAP | Common Alerting Protocol — standard format for emergency alerts |
| Data Diode | Hardware device allowing one-way data flow only |
| Federated Keys | Different signing keys for different alert tiers |
| FirstNet | Dedicated LTE network for first responders |
| HSM | Hardware Security Module — tamper-resistant key storage |
| IPAWS | Integrated Public Alert and Warning System (FEMA) |
| Mutual Aid | Agreement between jurisdictions to assist each other |
| Sovereign | Complete customer control over data and operations |

### B. Reference Documents

- CITYARRAY Security Design Document
- CITYARRAY Hardware Design Specification
- FEMA IPAWS CAP Profile
- NIST SP 800-57 (Key Management)
- NIST SP 800-82 (ICS Security)

### C. Contact

For questions about this specification:
- Technical: dev@cityarray.ai
- Security: security@cityarray.ai
- Sales: sales@cityarray.ai

---

*Document Version: 1.0*  
*Last Updated: December 2024*  
*Classification: Strategic Planning — Confidential*
