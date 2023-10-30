import torch

from features.features import SparseFeat, DenseFeat, VarlenFeat


# TODO: start+=feat['max_len'] powoduje blad, do sprawdzenia
class FeatureStore:
    def __init__(self, scheme_relations, scheme_items, scheme_users):
        self.tensor_id = 0
        self.edge_index = self._create_store(scheme_relations)
        self.item_feat = self._create_store(scheme_items)
        self.user_feat = self._create_store(scheme_users)

        self.dense_index = self.get_feature_index(DenseFeat)

    def _create_store(self, scheme):
        store = []
        for feat in scheme.features:
            if isinstance(feat, VarlenFeat):
                offset = feat.max_len
            else:
                offset = 1
            store.append(feat._replace(index=(self.tensor_id, self.tensor_id + offset)))
            self.tensor_id = self.tensor_id + offset

        # for feat_id, (feat_name, feat) in enumerate(scheme.items()):
        #     if feat['type'] == 'sparse':
        #         feat_cls = SparseFeat(
        #             feat_name,
        #             feat['emb_dim'],
        #             feat['num_emb'],
        #             feat['max_len'],
        #             feat_id,
        #             (self.tensor_id, self.tensor_id + feat['max_len'])
        #         )
        #         self.tensor_id = self.tensor_id + feat['max_len']
        #     elif feat['type'] == 'dense':
        #         feat_cls = DenseFeat(
        #             feat_name,
        #             feat_id,
        #             (self.tensor_id, self.tensor_id + 1)
        #         )
        #         self.tensor_id += 1
        #
        #     store.append(feat_cls)
        return store

    def features(self):
        return self.edge_index + self.user_feat + self.item_feat

    def get_input_dim(self):
        sparse_len = sum([f.emb_dim for f in self.get_feature_type(SparseFeat)])
        dense_len = len(self.get_feature_type(DenseFeat))
        return sparse_len + dense_len

    def get_feature_type(self, feat_type):
        return [f for f in self.features() if isinstance(f, feat_type)]

    def get_feature_index(self, feat_type):
        feats = self.get_feature_type(feat_type)

        if not feats:
            return torch.tensor([], dtype=torch.long)
        return torch.hstack([torch.arange(f.pad_index[0], f.pad_index[1]) for f in feats])