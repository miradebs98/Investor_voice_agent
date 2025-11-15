# 📸 Adding Miranda Presley Image

## Steps:

1. **Save the image file:**
   - Save your Miranda Presley image as: `pitch-perfect-ai/src/assets/miranda-presley.jpg`
   - (or `.png` if it's a PNG file)

2. **Update SelectPersona.tsx:**
   - Find this line (around line 7-9):
     ```typescript
     // import mirandaPresleyImage from "@/assets/miranda-presley.jpg";
     const mirandaPresleyImage = garryTanImage; // Placeholder
     ```
   - Replace with:
     ```typescript
     import mirandaPresleyImage from "@/assets/miranda-presley.jpg";
     ```

3. **Update Conversation.tsx:**
   - Find this line (around line 21-23):
     ```typescript
     // import mirandaPresleyImage from "@/assets/miranda-presley.jpg";
     const mirandaPresleyImage = garryTanImage; // Placeholder
     ```
   - Replace with:
     ```typescript
     import mirandaPresleyImage from "@/assets/miranda-presley.jpg";
     ```

4. **Restart frontend:**
   ```bash
   cd pitch-perfect-ai
   npm run dev
   ```

## Current Status:
✅ Code is ready - just needs the image file and import statements uncommented!
